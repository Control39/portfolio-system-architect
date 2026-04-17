"""
Модуль отслеживания карьерного прогресса пользователя.
Методология "Объективные маркеры компетенций"
© 2025 Ekaterina Kudelya. CC BY-ND 4.0
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Marker:
    id: str
    marker: str
    validation: str
    priority: str
    resources: List[str]
    smart_criteria: Dict[str, str]
    skill_name: Optional[str] = None
    methodology_author: str = "Ekaterina Kudelya"
    methodology_license: str = "CC BY-ND 4.0"

@dataclass
class SkillData:
    skill_name: str
    description: str
    levels: Dict[str, List[Marker]]

class CareerTracker:
    def __init__(self, markers_dir: str = "src/data/markers", progress_file: str = "src/data/user_progress.json"):
        self.markers_dir = Path(markers_dir)
        self.progress_file = Path(progress_file)
        self._markers_cache: Optional[Dict[str, SkillData]] = None
        self._all_markers_cache: Optional[Dict[str, Marker]] = None
        self.markers = self._load_all_markers()
        self.progress = self._load_progress()
    
    def _load_all_markers(self) -> Dict[str, SkillData]:
        if not self.markers_dir.exists():
            logger.warning(f"Директория маркеров не найдена: {self.markers_dir}")
            return {}
        
        markers = {}
        try:
            for file_path in self.markers_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        skill_data_raw = json.load(f)
                    
                    skill_name = skill_data_raw.get("skill_name", file_path.stem.capitalize())
                    levels = self._parse_skill_levels(skill_data_raw.get("levels", {}))
                    
                    markers[skill_name] = SkillData(
                        skill_name=skill_name,
                        description=skill_data_raw.get("description", ""),
                        levels=levels
                    )
                    logger.info(f"Загружен навык: {skill_name}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка парсинга JSON в файле {file_path}: {e}")
                except Exception as e:
                    logger.error(f"Неожиданная ошибка при загрузке {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Критическая ошибка при загрузке маркеров: {e}")
            
        return markers
    
    def _parse_skill_levels(self, levels_data: Dict[str, Any]) -> Dict[str, List[Marker]]:
        levels = {}
        for level_key, markers_list in levels_data.items():
            levels[level_key] = []
            for marker_data in markers_list:
                try:
                    marker = Marker(
                        id=marker_data["id"],
                        marker=marker_data["marker"],
                        validation=marker_data.get("validation", ""),
                        priority=marker_data.get("priority", "medium"),
                        resources=marker_data.get("resources", []),
                        smart_criteria=marker_data.get("smart_criteria", {}),
                        skill_name=marker_data.get("skill_name"),
                        methodology_author=marker_data.get("methodology_author", "Ekaterina Kudelya"),
                        methodology_license=marker_data.get("methodology_license", "CC BY-ND 4.0")
                    )
                    levels[level_key].append(marker)
                except KeyError as e:
                    logger.warning(f"Отсутствует ключ {e} в маркере: {marker_data}")
                    continue
        return levels
    
    def _load_progress(self) -> Dict[str, List[str]]:
        if not self.progress_file.exists():
            logger.info("Файл прогресса не найден, создаётся новый")
            return {"completed_markers": [], "in_progress_markers": []}
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                logger.warning("Некорректная структура файла прогресса")
                return {"completed_markers": [], "in_progress_markers": []}
            
            completed = data.get("completed_markers", [])
            in_progress = data.get("in_progress_markers", [])
            
            if not isinstance(completed, list) or not all(isinstance(x, str) for x in completed):
                logger.warning("Некорректные данные completed_markers")
                completed = []
                
            if not isinstance(in_progress, list) or not all(isinstance(x, str) for x in in_progress):
                logger.warning("Некорректные данные in_progress_markers")
                in_progress = []
            
            logger.info(f"Загружен прогресс: {len(completed)} выполнено, {len(in_progress)} в процессе")
            return {"completed_markers": completed, "in_progress_markers": in_progress}
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга файла прогресса: {e}")
            return {"completed_markers": [], "in_progress_markers": []}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке прогресса: {e}")
            return {"completed_markers": [], "in_progress_markers": []}
    
    def _save_progress(self) -> bool:
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
            logger.info("Прогресс успешно сохранён")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения прогресса: {e}")
            return False
    
    def show_progress(self) -> None:
        print("\n📊 ВАШ ПРОГРЕСС:")
        print("-" * 50)
        
        if not self.markers:
            print("⚠️ Нет загруженных маркеров.")
            return
        
        total_completed = 0
        total_markers = 0
        
        for skill_name, skill_data in self.markers.items():
            completed_count = 0
            skill_total = 0
            
            for level_markers in skill_data.levels.values():
                skill_total += len(level_markers)
                for marker in level_markers:
                    if marker.id in self.progress["completed_markers"]:
                        completed_count += 1
            
            if skill_total == 0:
                continue
                
            total_completed += completed_count
            total_markers += skill_total
            
            percentage = (completed_count / skill_total) * 100
            progress_bar = self._create_progress_bar(percentage)
            print(f"{skill_name:<20} {progress_bar} {percentage:5.1f}% ({completed_count}/{skill_total})")
        
        if total_markers > 0:
            overall_percentage = (total_completed / total_markers) * 100
            overall_bar = self._create_progress_bar(overall_percentage)
            print(f"{'Общий прогресс':<20} {overall_bar} {overall_percentage:5.1f}% ({total_completed}/{total_markers})")
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        filled_width = int((percentage / 100) * width)
        return "█" * filled_width + "░" * (width - filled_width)
    
    def mark_completed(self, marker_id: str) -> bool:
        marker_id = marker_id.strip()
        
        if not marker_id:
            print("❌ ID маркера не может быть пустым")
            return False
        
        if marker_id in self.progress["completed_markers"]:
            print(f"ℹ️ Маркер {marker_id} уже отмечен как выполненный")
            return True
        
        if not self._marker_exists(marker_id):
            print(f"❌ Маркер {marker_id} не найден.")
            return False
        
        self.progress["completed_markers"].append(marker_id)
        
        if marker_id in self.progress["in_progress_markers"]:
            self.progress["in_progress_markers"].remove(marker_id)
        
        if self._save_progress():
            print(f"✅ Маркер {marker_id} отмечен как выполненный! 🎉")
            return True
        else:
            print("❌ Ошибка при сохранении прогресса")
            return False
    
    def _marker_exists(self, marker_id: str) -> bool:
        for skill_data in self.markers.values():
            for level_markers in skill_data.levels.values():
                for marker in level_markers:
                    if marker.id == marker_id:
                        return True
        return False
    
    def show_recommendations(self, limit: int = 5) -> None:
        print("\n🎯 РЕКОМЕНДАЦИИ (high priority):")
        print("-" * 50)
        
        high_priority_markers = []
        for skill_name, skill_data in self.markers.items():
            for level_markers in skill_data.levels.values():
                for marker in level_markers:
                    if (marker.id not in self.progress["completed_markers"] and marker.priority == "high"):
                        high_priority_markers.append((skill_name, marker))
        
        if not high_priority_markers:
            print("🎉 Поздравляем! Все high-priority маркеры выполнены!")
            return
        
        shown_count = 0
        for skill_name, marker in high_priority_markers[:limit]:
            print(f"• {skill_name}: {marker.marker}")
            
            if marker.resources:
                print(f" 📎 Ресурсы: {', '.join(marker.resources[:2])}")
                if len(marker.resources) > 2:
                    print(f" ... и ещё {len(marker.resources) - 2} ресурсов")
            
            if marker.smart_criteria:
                time_bound = marker.smart_criteria.get("time_bound", "")
                if time_bound:
                    print(f" ⏰ Время выполнения: {time_bound}")
            print()
            
            shown_count += 1
            
            if shown_count >= limit:
                remaining = len(high_priority_markers) - limit
                if remaining > 0:
                    print(f"... и ещё {remaining} рекомендаций")
                break
    
    def get_skill_progress(self, skill_name: str) -> Dict[str, Any]:
        skill_data = self.markers.get(skill_name)
        if not skill_data:
            return None
        
        completed = []
        total = 0
        
        for level_key, level_markers in skill_data.levels.items():
            level_total = len(level_markers)
            level_completed = 0
            
            for marker in level_markers:
                total += 1
                if marker.id in self.progress["completed_markers"]:
                    completed.append(marker)
                    level_completed += 1
        
        overall_percentage = (len(completed) / total * 100) if total > 0 else 0
        
        return {
            "skill_name": skill_name,
            "completed_count": len(completed),
            "total_count": total,
            "percentage": overall_percentage,
            "completed_markers": [m.id for m in completed],
            "levels": skill_data.levels
        }

__all__ = ['CareerTracker', 'Marker', 'SkillData']
