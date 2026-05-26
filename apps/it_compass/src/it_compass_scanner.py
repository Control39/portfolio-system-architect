#/usr/bin/env python3
"""
IT Compass Scanner - Автоматическое сканирование маркеров компетенций

Использует АВТОРСКИЕ маркеры Ekaterina Kudelya из apps/it_compass/

Сканирует проект и:
1. Загружает маркеры из apps/it_compass/src/data/markers/*.json
2. Проверяет наличие артефактов в проекте
3. Интегрируется с CareerTracker
4. Генерирует портфолио через AI
5. Даёт карьерные советы

Интеграция с Cognitive Agent и AI Provider Manager
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from apps.ai_provider_manager.src.ai_provider_manager import chat_with_fallback, get_provider_manager
from apps.it_compass.src.core.tracker import CareerTracker

# Настройка логирования
logs_dir = REPO_ROOT / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "it_compass_scanner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ITCompassScanner:
    """
    Сканер маркеров компетенций IT Compass
    
    Использует АВТОРСКИЕ маркеры Ekaterina Kudelya из apps/it_compass/
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else REPO_ROOT
        self.it_compass_core = self.project_path / "apps" / "it_compass"
        self.markers_dir = self.it_compass_core / "src" / "data" / "markers"
        self.compass_dir = self.project_path / "it_compass"
        self.progress_file = self.compass_dir / "progress.json"
        self.portfolio_file = self.compass_dir / "portfolio.json"
        
        # Инициализация
        self.ai_manager = get_provider_manager()
        
        # Используем АВТОРСКИЙ CareerTracker
        self.tracker = CareerTracker()
        
        # Загружаем авторские маркеры
        self.author_markers = self._load_author_markers()
        
        logger.info(f"🧭 IT Compass Scanner initialized")
        logger.info(f"📁 Project path: {self.project_path}")
        logger.info(f"📚 Using author markers from: {self.markers_dir}")
        logger.info(f"👤 Author: Ekaterina Kudelya (CC BY-ND 4.0)")
        logger.info(f"📊 Loaded {len(self.author_markers)} marker files")
    
    def _load_author_markers(self) -> List[Dict[str, Any]]:
        """Загрузить авторские маркеры из JSON файлов"""
        markers = []
        
        if not self.markers_dir.exists():
            logger.warning(f"Markers directory not found: {self.markers_dir}")
            return markers
        
        for json_file in self.markers_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                    markers.append(data)
                    logger.debug(f"Loaded: {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        return markers
    
    def scan_project(self) -> Dict[str, Any]:
        """Сканировать проект на наличие артефактов маркеров"""
        logger.info("🔍 Starting IT Compass scan...")
        
        scan_start = datetime.now()
        
        # Получаем прогресс из CareerTracker
        tracker_progress = self.tracker.calculate_progress()
        
        # Сканируем проект на наличие артефактов
        artifacts = self._scan_for_artifacts()
        
        # Расчёт прогресса на основе артефактов
        artifact_progress = self._calculate_artifact_progress(artifacts)
        
        # Объединяем результаты
        self.scan_results = {
            "timestamp": scan_start.isoformat(),
            "tracker_progress": tracker_progress,
            "artifact_progress": artifact_progress,
            "artifacts": artifacts,
            "markers_loaded": len(self.author_markers),
            "methodology_author": "Ekaterina Kudelya",
            "methodology_license": "CC BY-ND 4.0"
        }
        
        # Генерация портфолио через AI
        self._generate_portfolio()
        
        # Сохранение результатов
        self._save_results()
        
        scan_duration = (datetime.now() - scan_start).total_seconds()
        
        logger.info(f"✅ Scan completed in {scan_duration:.2f}s")
        logger.info(f"   Markers loaded: {len(self.author_markers)}")
        logger.info(f"   Artifacts found: {sum(len(v) for v in artifacts.values())}")
        logger.info(f"   Tracker progress: {tracker_progress['overall_progress']:.1f}%")
        
        return self.scan_results
    
    def _scan_for_artifacts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Сканировать проект на наличие артефактов"""
        logger.info("  🔍 Scanning for artifacts...")
        
        artifacts = {
            "python": [],
            "tests": [],
            "docker": [],
            "docs": [],
            "architecture": [],
            "system_thinking": []
        }
        
        # Python файлы
        py_files = list(self.project_path.rglob("**/*.py"))
        if len(py_files) >= 10:
            artifacts["python"].append({
                "type": "python_files",
                "count": len(py_files),
                "evidence": f"{len(py_files)} Python files found"
            })
        
        # Тесты
        test_files = list(self.project_path.rglob("**/test_*.py"))
        if len(test_files) >= 5:
            artifacts["tests"].append({
                "type": "unit_tests",
                "count": len(test_files),
                "evidence": f"{len(test_files)} test files found"
            })
        
        e2e_dir = self.project_path / "tests" / "e2e"
        if e2e_dir.exists():
            e2e_files = list(e2e_dir.glob("test_*.py"))
            if e2e_files:
                artifacts["tests"].append({
                    "type": "e2e_tests",
                    "count": len(e2e_files),
                    "evidence": f"{len(e2e_files)} E2E tests found"
                })
        
        # Docker
        docker_compose = self.project_path / "docker-compose.yml"
        if docker_compose.exists():
            artifacts["docker"].append({
                "type": "docker_compose",
                "evidence": "docker-compose.yml found"
            })
        
        # Документация
        docs_dir = self.project_path / "docs"
        if docs_dir.exists():
            md_files = list(docs_dir.glob("**/*.md"))
            if md_files:
                artifacts["docs"].append({
                    "type": "documentation",
                    "count": len(md_files),
                    "evidence": f"{len(md_files)} markdown files"
                })
        
        # Архитектура
        apps_dir = self.project_path / "apps"
        if apps_dir.exists():
            services = list(apps_dir.iterdir())
            if len(services) >= 3:
                artifacts["architecture"].append({
                    "type": "microservices",
                    "count": len(services),
                    "evidence": [s.name for s in services[:5]]
                })
        
        # Системное мышление - IT Compass
        if self.it_compass_core.exists():
            artifacts["system_thinking"].append({
                "type": "it_compass_methodology",
                "evidence": "IT Compass core found (author methodology)"
            })
            
            # Проверка на маркеры системного мышления
            system_thinking_file = self.markers_dir / "system_thinking.json"
            if system_thinking_file.exists():
                artifacts["system_thinking"].append({
                    "type": "system_thinking_markers",
                    "evidence": "System Thinking markers defined"
                })
        
        # Логирование
        for category, items in artifacts.items():
            if items:
                logger.info(f"   ✅ {category}: {len(items)} artifacts")
        
        return artifacts
    
    def _calculate_artifact_progress(self, artifacts: Dict[str, List]) -> Dict[str, Any]:
        """Рассчитать прогресс на основе артефактов"""
        total_categories = len(artifacts)
        categories_with_artifacts = sum(1 for v in artifacts.values() if v)
        
        return {
            "overall": (categories_with_artifacts / total_categories * 100) if total_categories > 0 else 0,
            "categories": {
                cat: (len(items) / 3 * 100) if items else 0
                for cat, items in artifacts.items()
            }
        }
    
    def _generate_portfolio(self):
        """Генерация портфолио через AI с пониманием контекста"""
        logger.info("  📝 Generating portfolio...")
        
        if not self.ai_manager.get_active_provider():
            logger.warning("AI provider not available, skipping portfolio generation")
            return
        
        # Чтение README и документации для понимания контекста
        context = self._read_project_context()
        
        # Подготовка контекста с акцентом на методологию
        portfolio_context = {
            "author": "Ekaterina Kudelya",
            "methodology": "IT Compass - система объективных маркеров компетенций",
            "markers_loaded": len(self.author_markers),
            "tracker_progress": self.scan_results.get("tracker_progress", {}),
            "artifacts_found": sum(len(v) for v in self.scan_results.get("artifacts", {}).values()),
            "project_context": context,
            "note": "Автор - методолог и архитектор когнитивных систем, не чистый разработчик"
        }
        
        prompt = f"""
На основе сканирования проекта сгенерируй карьерные рекомендации.

ВАЖНО: Автор проекта (Ekaterina Kudelya) - это НЕ чистый разработчик, а **методолог и архитектор когнитивных систем**.
Она создала IT Compass - методологию для решения проблемы карьерной неопределённости.

Контекст проекта:
{json.dumps(context, indent=2, ensure_ascii=False, default=str)}

Методология и артефакты:
{json.dumps(portfolio_context, indent=2, ensure_ascii=False, default=str)}

Сгенерируй портфолио в формате JSON:
{{
  "summary": "Краткое описание уникальной компетенции автора",
  "strengths": ["Сильные стороны (методология, архитектура, системное мышление)"],
  "career_profile": "Уникальный карьерный профиль (гибридная роль)",
  "job_recommendations": [
    {{
      "title": "Название вакансии",
      "level": "Уровень (Junior/Middle/Senior/Lead)",
      "why": "Почему подходит (связь с методологией и проектом)",
      "priority": "high/medium/low"
    }}
  ],
  "next_markers": ["Какие маркеры из IT Compass достичь дальше для карьерного роста"]
}}

Вакансии должны отражать гибридную роль: методология + архитектура + управление + AI
"""
        
        response = chat_with_fallback([
            {"role": "system", "content": "Ты — карьерный консультант для специалистов с нетрадиционным путём. Ты понимаешь ценность методологии, системного мышления и архитектуры когнитивных систем."},
            {"role": "user", "content": prompt}
        ])
        
        if response:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    portfolio = json.loads(json_match.group())
                    self.scan_results["portfolio"] = portfolio
                    logger.info("✅ Portfolio generated with career recommendations")
                else:
                    logger.warning("Failed to parse portfolio JSON")
            except Exception as e:
                logger.warning(f"Failed to parse portfolio JSON: {e}")
    
    def _read_project_context(self) -> Dict[str, Any]:
        """Прочитать проект и понять контекст (README, docs, ADR)"""
        context = {
            "readme_summary": "",
            "author_profile": "",
            "project_purpose": "",
            "key_themes": []
        }
        
        # Прочитать главный README
        main_readme = self.project_path / "README.md"
        if main_readme.exists():
            try:
                content = main_readme.read_text(encoding="utf-8-sig")[:5000]
                context["readme_summary"] = "Main README exists - large portfolio system"
            except:
                pass
        
        # Прочитать README IT Compass
        compass_readme = self.it_compass_core / "README.md"
        if compass_readme.exists():
            try:
                content = compass_readme.read_text(encoding="utf-8-sig")
                if "карьерной неопределенности" in content.lower() or "career uncertainty" in content.lower():
                    context["project_purpose"] = "Решение проблемы карьерной неопределённости"
                if "методология" in content.lower():
                    context["author_profile"] = "Методолог и архитектор систем"
            except:
                pass
        
        # Проверить ADR
        adr_dir = self.project_path / "docs" / "architecture" / "decisions"
        if adr_dir.exists():
            adr_files = list(adr_dir.glob("*.md"))
            if adr_files:
                context["key_themes"].append("Архитектурные решения задокументированы")
        
        # Проверить экосистему проектов
        apps_dir = self.project_path / "apps"
        if apps_dir.exists():
            projects = [d.name for d in apps_dir.iterdir() if d.is_dir()]
            context["ecosystem"] = projects
            context["key_themes"].append(f"Микросервисная экосистема: {len(projects)} проектов")
        
        # Ключевые темы
        context["key_themes"].extend([
            "Системное мышление",
            "Методология объективных маркеров",
            "Архитектура когнитивных систем",
            "Управление AI-агентами"
        ])
        
        return context
    
    def _save_results(self):
        """Сохранить результаты сканирования"""
        self.compass_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем прогресс
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        # Сохраняем портфолио
        if "portfolio" in self.scan_results:
            with open(self.portfolio_file, "w", encoding="utf-8") as f:
                json.dump(self.scan_results["portfolio"], f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to {self.compass_dir}")
    
    def get_recommendations(self) -> List[str]:
        """Получить карьерные рекомендации"""
        if "portfolio" not in self.scan_results:
            self._generate_portfolio()
        
        return self.scan_results.get("portfolio", {}).get("career_recommendations", [])
    
    def get_next_markers(self) -> List[str]:
        """Получить список следующих маркеров для достижения"""
        if "portfolio" not in self.scan_results:
            self._generate_portfolio()
        
        return self.scan_results.get("portfolio", {}).get("next_markers", [])
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус IT Compass"""
        return {
            "project_path": str(self.project_path),
            "markers_loaded": len(self.author_markers),
            "methodology_author": "Ekaterina Kudelya",
            "methodology_license": "CC BY-ND 4.0",
            "tracker_progress": self.scan_results.get("tracker_progress", {}),
            "last_scan": self.scan_results.get("timestamp")
        }


# Глобальный экземпляр
_scanner: Optional[ITCompassScanner] = None


def get_scanner() -> ITCompassScanner:
    """Получить глобальный экземпляр сканера"""
    global _scanner
    if _scanner is None:
        _scanner = ITCompassScanner()
    return _scanner


def scan_it_compass(project_path: str = None) -> Dict[str, Any]:
    """Удобная функция для сканирования IT Compass"""
    scanner = ITCompassScanner(project_path)
    return scanner.scan_project()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="IT Compass Scanner")
    parser.add_argument("--scan", action="store_true", help="Запустить сканирование")
    parser.add_argument("--status", action="store_true", help="Показать статус")
    parser.add_argument("--project", type=str, help="Путь к проекту")
    
    args = parser.parse_args()
    
    if args.scan:
        scanner = ITCompassScanner(project_path=args.project)
        results = scanner.scan_project()
        print(f"\n✅ Scan completed!")
        print(f"   Markers loaded: {results['markers_loaded']}")
        print(f"   Tracker progress: {results['tracker_progress']['overall_progress']:.1f}%")
    
    elif args.status:
        scanner = get_scanner()
        status = scanner.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()
