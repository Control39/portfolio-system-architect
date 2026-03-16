#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт автоматической синхронизации кейса с IT-Compass
Автоматизирует процесс интеграции кейсов с маркерами IT-Compass
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ITCompassSync:
    def __init__(
        self,
        case_path: str,
        it_compass_path: str = "components/it-compass",
        portfolio_path: str = "components/portfolio-organizer"
    ):
        self.case_path = Path(case_path)
        self.it_compass_path = Path(it_compass_path)
        self.portfolio_path = Path(portfolio_path)
        self.mapping_file = self.case_path / "markers-mapping.json"
        
    def sync_case_to_it_compass(self) -> bool:
        """Синхронизирует кейс с маркерами IT-Compass"""
        try:
            # 1. Чтение mapping-файла кейса
            if not self.mapping_file.exists():
                logger.error(f"Файл {self.mapping_file} не найден")
                return False
                
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
            
            # 2. Обновление src/data/markers/[skill].json в it-compass
            updated_markers = self._update_it_compass_markers(mapping_data)
            
            # 3. Генерация отчёта о прогрессе
            self._generate_progress_report(mapping_data, updated_markers)
            
            # 4. Обновление портфолио через portfolio-organizer
            self._update_portfolio(mapping_data)
            
            logger.info("Синхронизация кейса с IT-Compass завершена успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при синхронизации кейса: {e}")
            return False
    
    def _update_it_compass_markers(self, mapping_data: Dict) -> List[str]:
        """Обновляет маркеры в IT-Compass"""
        updated_markers = []
        
        # Путь к директории маркеров
        markers_dir = self.it_compass_path / "src" / "data" / "markers"
        
        if not markers_dir.exists():
            logger.warning(f"Директория маркеров {markers_dir} не найдена")
            return updated_markers
        
        # Для каждого маркера в mapping-файле
        for marker_mapping in mapping_data.get("mapped_markers", []):
            marker_id = marker_mapping.get("marker_id")
            skill = marker_mapping.get("skill")
            
            if not marker_id or not skill:
                continue
                
            # Путь к файлу маркеров навыка
            skill_file = markers_dir / f"{skill}.json"
            
            if not skill_file.exists():
                logger.warning(f"Файл маркеров {skill_file} не найден")
                continue
            
            # Чтение существующих маркеров
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга файла {skill_file}: {e}")
                continue
            
            # Поиск и обновление маркера
            marker_updated = False
            for level_data in skill_data.get("levels", {}).values():
                for marker in level_data:
                    if marker.get("id") == marker_id:
                        # Обновление информации о маркере
                        marker["validation_status"] = marker_mapping.get("validation_status", "pending_review")
                        marker["auto_verified"] = marker_mapping.get("auto_verified", False)
                        marker_updated = True
                        updated_markers.append(marker_id)
                        break
            
            # Сохранение обновленных маркеров
            if marker_updated:
                try:
                    with open(skill_file, 'w', encoding='utf-8') as f:
                        json.dump(skill_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"Ошибка сохранения файла {skill_file}: {e}")
        
        return updated_markers
    
    def _generate_progress_report(self, mapping_data: Dict, updated_markers: List[str]):
        """Генерирует отчёт о прогрессе"""
        report_data = {
            "case_id": mapping_data.get("case_id"),
            "case_title": mapping_data.get("case_title"),
            "updated_markers": updated_markers,
            "total_markers": len(mapping_data.get("mapped_markers", [])),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        report_file = self.case_path / "sync_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Отчёт о синхронизации сохранен: {report_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отчёта: {e}")
    
    def _update_portfolio(self, mapping_data: Dict):
        """Обновляет портфолио через portfolio-organizer"""
        portfolio_file = self.portfolio_path / "src" / "generated" / f"{mapping_data.get('case_id')}.md"
        
        # Создание директории если не существует
        portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Генерация содержимого портфолио
        portfolio_content = self._generate_portfolio_content(mapping_data)
        
        try:
            with open(portfolio_file, 'w', encoding='utf-8') as f:
                f.write(portfolio_content)
            logger.info(f"Файл портфолио сохранен: {portfolio_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения портфолио: {e}")
    
    def _generate_portfolio_content(self, mapping_data: Dict) -> str:
        """Генерирует содержимое файла портфолио"""
        content = [
            f"# {mapping_data.get('case_title', '')}",
            "",
            f"**ID кейса:** {mapping_data.get('case_id', '')}",
            "",
            "## Связанные маркеры компетенций",
            ""
        ]
        
        for marker in mapping_data.get("mapped_markers", []):
            content.extend([
                f"### {marker.get('marker_id', '')}",
                f"- **Навык:** {marker.get('skill', '')}",
                f"- **Уровень:** {marker.get('level', '')}",
                f"- **Статус валидации:** {marker.get('validation_status', '')}",
                f"- **Описание:** {marker.get('evidence', {}).get('description', '')}",
                ""
            ])
        
        content.extend([
            "## Точки интеграции",
            ""
        ])
        
        for point_name, point_path in mapping_data.get("integration_points", {}).items():
            content.append(f"- **{point_name}:** {point_path}")
        
        return "\n".join(content)


def sync_case_to_it_compass(case_path: str, markers_file: str = "markers-mapping.json") -> bool:
    """Синхронизирует кейс с маркерами IT-Compass"""
    sync_tool = ITCompassSync(case_path)
    return sync_tool.sync_case_to_it_compass()


if __name__ == "__main__":
    import argparse
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Синхронизация кейса с IT-Compass')
    parser.add_argument('case_path', help='Путь к директории кейса')
    parser.add_argument('--markers-file', default='markers-mapping.json',
                        help='Имя файла с маппингом маркеров (по умолчанию: markers-mapping.json)')
    
    args = parser.parse_args()
    
    success = sync_case_to_it_compass(args.case_path, args.markers_file)
    
    if success:
        print("✅ Синхронизация кейса с IT-Compass завершена успешно")
        sys.exit(0)
    else:
        print("❌ Ошибка синхронизации кейса с IT-Compass")
        sys.exit(1)