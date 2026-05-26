#!/usr/bin/env python3
"""
IT Compass Scanner - Автоматическое сканирование маркеров компетенций

Сканирует проект и:
1. Находит маркеры компетенций (код, тесты, документация)
2. Обновляет прогресс в IT Compass
3. Генерирует портфолио
4. Дает карьерные советы

Интеграция с Cognitive Agent и AI Provider Manager
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Добавляем корень проекта в PATH
REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from apps.ai_provider_manager.src.ai_provider_manager import chat_with_fallback, get_provider_manager
from apps.ai_config_manager.src.config_manager import ConfigManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(REPO_ROOT / "logs" / "it_compass_scanner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Marker:
    """Маркер компетенции"""
    id: str
    name: str
    category: str
    description: str
    level: str  # beginner, intermediate, advanced, expert
    weight: float  # Веса для расчета прогресса
    detected: bool = False
    evidence: List[str] = None
    confidence: float = 0.0
    last_verified: Optional[str] = None


class ITCompassScanner:
    """
    Сканер маркеров компетенций IT Compass
    
    Пример использования:
    ```python
    scanner = ITCompassScanner()
    results = scanner.scan_project()
    ```
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else REPO_ROOT
        self.compass_dir = self.project_path / "it_compass"
        self.markers_file = self.compass_dir / "markers.json"
        self.progress_file = self.compass_dir / "progress.json"
        self.portfolio_file = self.compass_dir / "portfolio.json"
        
        # Инициализация
        self.config = ConfigManager()
        self.ai_manager = get_provider_manager()
        
        # Маркеры компетенций
        self.markers: Dict[str, Marker] = {}
        self.progress: Dict[str, Any] = {}
        
        # Инициализация маркеров
        self._init_markers()
        
        logger.info(f"🧭 IT Compass Scanner initialized")
        logger.info(f"📁 Project path: {self.project_path}")
    
    def _init_markers(self):
        """Инициализация маркеров компетенций"""
        
        # Технические навыки
        self.markers = {
            # Архитектура и дизайн
            "arch_microservices": Marker(
                id="arch_microservices",
                name="Микросервисная архитектура",
                category="architecture",
                description="Проектирование и реализация микросервисов",
                level="advanced",
                weight=10.0
            ),
            "arch_domain_driven": Marker(
                id="arch_domain_driven",
                name="DDD (Domain-Driven Design)",
                category="architecture",
                description="Применение паттернов DDD",
                level="advanced",
                weight=10.0
            ),
            "arch_cqrs": Marker(
                id="arch_cqrs",
                name="CQRS паттерн",
                category="architecture",
                description="Разделение операций чтения и записи",
                level="advanced",
                weight=8.0
            ),
            
            # Разработка
            "dev_python": Marker(
                id="dev_python",
                name="Python разработка",
                category="development",
                description="Продвинутый Python",
                level="intermediate",
                weight=5.0
            ),
            "dev_async": Marker(
                id="dev_async",
                name="Асинхронное программирование",
                category="development",
                description="async/await, asyncio",
                level="advanced",
                weight=7.0
            ),
            "dev_api": Marker(
                id="dev_api",
                name="REST API разработка",
                category="development",
                description="Проектирование и реализация API",
                level="intermediate",
                weight=6.0
            ),
            
            # Тестирование
            "test_unit": Marker(
                id="test_unit",
                name="Модульное тестирование",
                category="testing",
                description="Написание unit-тестов",
                level="intermediate",
                weight=5.0
            ),
            "test_e2e": Marker(
                id="test_e2e",
                name="E2E тестирование",
                category="testing",
                description="End-to-end тестирование",
                level="advanced",
                weight=8.0
            ),
            "test_tdd": Marker(
                id="test_tdd",
                name="TDD (Test-Driven Development)",
                category="testing",
                description="Разработка через тестирование",
                level="advanced",
                weight=7.0
            ),
            
            # DevOps
            "ops_docker": Marker(
                id="ops_docker",
                name="Docker контейнеризация",
                category="devops",
                description="Работа с Docker",
                level="intermediate",
                weight=5.0
            ),
            "ops_ci_cd": Marker(
                id="ops_ci_cd",
                name="CI/CD пайплайны",
                category="devops",
                description="Автоматизация сборки и деплоя",
                level="advanced",
                weight=8.0
            ),
            "ops_monitoring": Marker(
                id="ops_monitoring",
                name="Мониторинг и логирование",
                category="devops",
                description="Настройка мониторинга",
                level="intermediate",
                weight=5.0
            ),
            
            # Безопасность
            "sec_auth": Marker(
                id="sec_auth",
                name="Аутентификация и авторизация",
                category="security",
                description="JWT, OAuth2, роль-based доступ",
                level="advanced",
                weight=8.0
            ),
            "sec_crypto": Marker(
                id="sec_crypto",
                name="Криптография",
                category="security",
                description="Хеширование, шифрование",
                level="intermediate",
                weight=6.0
            ),
            
            # Документация
            "doc_api": Marker(
                id="doc_api",
                name="API документация",
                category="documentation",
                description="OpenAPI/Swagger спецификации",
                level="intermediate",
                weight=4.0
            ),
            "doc_adr": Marker(
                id="doc_adr",
                name="ADR (Architecture Decision Records)",
                category="documentation",
                description="Документирование архитектурных решений",
                level="advanced",
                weight=6.0
            ),
        }
    
    def scan_project(self) -> Dict[str, Any]:
        """Сканировать проект на наличие маркеров"""
        logger.info("🔍 Starting IT Compass scan...")
        
        scan_start = datetime.now()
        
        # Сброс маркеров
        for marker in self.markers.values():
            marker.detected = False
            marker.evidence = []
            marker.confidence = 0.0
        
        # Сканирование по категориям
        self._scan_architecture()
        self._scan_development()
        self._scan_testing()
        self._scan_devops()
        self._scan_security()
        self._scan_documentation()
        
        # Расчет прогресса
        self._calculate_progress()
        
        # Генерация портфолио
        self._generate_portfolio()
        
        # Сохранение результатов
        self._save_results()
        
        scan_duration = (datetime.now() - scan_start).total_seconds()
        
        logger.info(f"✅ Scan completed in {scan_duration:.2f}s")
        logger.info(f"   Markers detected: {self._count_detected_markers()}")
        logger.info(f"   Progress: {self.progress.get('overall', 0):.1f}%")
        
        return {
            "timestamp": scan_start.isoformat(),
            "markers_detected": self._count_detected_markers(),
            "markers_total": len(self.markers),
            "progress": self.progress,
            "markers": {k: asdict(v) for k, v in self.markers.items()}
        }
    
    def _scan_architecture(self):
        """Сканирование архитектурных маркеров"""
        logger.info("  🔍 Scanning architecture...")
        
        # Микросервисы
        if (self.project_path / "apps").exists():
            apps = list((self.project_path / "apps").iterdir())
            if len(apps) >= 3:
                marker = self.markers["arch_microservices"]
                marker.detected = True
                marker.evidence = [str(a.name) for a in apps[:5]]
                marker.confidence = min(0.5 + (len(apps) * 0.1), 1.0)
        
        # DDD
        patterns = ["domain", "application", "infrastructure", "entity.py", "repository.py"]
        for pattern in patterns:
            if list(self.project_path.rglob(f"**/{pattern}")):
                marker = self.markers["arch_domain_driven"]
                marker.detected = True
                marker.evidence.append(pattern)
                marker.confidence = 0.7
                break
        
        # CQRS
        if list(self.project_path.rglob("**/commands.py")) or \
           list(self.project_path.rglob("**/queries.py")):
            marker = self.markers["arch_cqrs"]
            marker.detected = True
            marker.evidence.append("commands/queries separation")
            marker.confidence = 0.8
    
    def _scan_development(self):
        """Сканирование маркеров разработки"""
        logger.info("  🔍 Scanning development...")
        
        # Python
        py_files = list(self.project_path.rglob("**/*.py"))
        if len(py_files) >= 10:
            marker = self.markers["dev_python"]
            marker.detected = True
            marker.evidence.append(f"{len(py_files)} Python files")
            marker.confidence = min(0.5 + (len(py_files) * 0.01), 1.0)
        
        # Async
        async_patterns = ["async def", "asyncio", "aiohttp", "fastapi"]
        for file in py_files[:50]:  # Проверяем первые 50 файлов
            try:
                content = file.read_text(encoding="utf-8")
                for pattern in async_patterns:
                    if pattern in content:
                        marker = self.markers["dev_async"]
                        marker.detected = True
                        marker.evidence.append(pattern)
                        marker.confidence = 0.8
                        break
            except:
                pass
        
        # API
        if (self.project_path / "apps" / "auth_service").exists() or \
           (self.project_path / "apps" / "infra_orchestrator").exists():
            marker = self.markers["dev_api"]
            marker.detected = True
            marker.evidence.append("REST services found")
            marker.confidence = 0.9
    
    def _scan_testing(self):
        """Сканирование маркеров тестирования"""
        logger.info("  🔍 Scanning testing...")
        
        # Unit tests
        test_files = list(self.project_path.rglob("**/test_*.py"))
        if len(test_files) >= 5:
            marker = self.markers["test_unit"]
            marker.detected = True
            marker.evidence.append(f"{len(test_files)} test files")
            marker.confidence = min(0.5 + (len(test_files) * 0.02), 1.0)
        
        # E2E tests
        e2e_dir = self.project_path / "tests" / "e2e"
        if e2e_dir.exists():
            e2e_files = list(e2e_dir.glob("test_*.py"))
            if e2e_files:
                marker = self.markers["test_e2e"]
                marker.detected = True
                marker.evidence.append(f"{len(e2e_files)} E2E tests")
                marker.confidence = 0.9
        
        # TDD (конвенция test-first)
        pytest_ini = self.project_path / "pytest.ini"
        if pytest_ini.exists():
            marker = self.markers["test_tdd"]
            marker.detected = True
            marker.evidence.append("pytest configured")
            marker.confidence = 0.7
    
    def _scan_devops(self):
        """Сканирование DevOps маркеров"""
        logger.info("  🔍 Scanning DevOps...")
        
        # Docker
        docker_files = [
            self.project_path / "Dockerfile",
            self.project_path / "docker-compose.yml"
        ]
        docker_found = any(f.exists() for f in docker_files)
        if docker_found:
            marker = self.markers["ops_docker"]
            marker.detected = True
            marker.evidence.append("docker-compose.yml")
            marker.confidence = 0.9
        
        # CI/CD
        ci_files = [
            self.project_path / ".github" / "workflows",
            self.project_path / ".gitlab-ci.yml"
        ]
        ci_found = any(f.exists() for f in ci_files)
        if ci_found:
            marker = self.markers["ops_ci_cd"]
            marker.detected = True
            marker.evidence.append("CI/CD configuration")
            marker.confidence = 0.85
        
        # Monitoring
        if list(self.project_path.rglob("**/*monitor*")) or \
           list(self.project_path.rglob("**/jaeger*")):
            marker = self.markers["ops_monitoring"]
            marker.detected = True
            marker.evidence.append("Monitoring infrastructure")
            marker.confidence = 0.7
    
    def _scan_security(self):
        """Сканирование маркеров безопасности"""
        logger.info("  🔍 Scanning security...")
        
        # Auth
        auth_files = [
            self.project_path / "apps" / "auth_service",
            self.project_path / "**" / "jwt*.py",
            self.project_path / "**" / "auth*.py"
        ]
        auth_found = any(f.exists() or list(f.parent.glob(f.name)) for f in auth_files[:1])
        if auth_found or list(self.project_path.rglob("**/jwt*.py")):
            marker = self.markers["sec_auth"]
            marker.detected = True
            marker.evidence.append("Authentication service")
            marker.confidence = 0.85
        
        # Crypto
        crypto_patterns = ["hashlib", "cryptography", "bcrypt", "passlib"]
        for file in self.project_path.rglob("**/*.py"):
            try:
                content = file.read_text(encoding="utf-8")
                for pattern in crypto_patterns:
                    if pattern in content:
                        marker = self.markers["sec_crypto"]
                        marker.detected = True
                        marker.evidence.append(pattern)
                        marker.confidence = 0.8
                        break
            except:
                pass
    
    def _scan_documentation(self):
        """Сканирование маркеров документации"""
        logger.info("  🔍 Scanning documentation...")
        
        # API docs
        if (self.project_path / "docs").exists():
            api_docs = list((self.project_path / "docs").glob("*api*.md"))
            if api_docs:
                marker = self.markers["doc_api"]
                marker.detected = True
                marker.evidence.append(f"{len(api_docs)} API docs")
                marker.confidence = 0.75
        
        # ADR
        adr_dir = self.project_path / "docs" / "adr"
        if adr_dir.exists():
            adr_files = list(adr_dir.glob("*.md"))
            if adr_files:
                marker = self.markers["doc_adr"]
                marker.detected = True
                marker.evidence.append(f"{len(adr_files)} ADRs")
                marker.confidence = 0.9
    
    def _calculate_progress(self):
        """Расчет общего прогресса"""
        total_weight = sum(m.weight for m in self.markers.values())
        detected_weight = sum(
            m.weight * m.confidence 
            for m in self.markers.values() 
            if m.detected
        )
        
        # Общий прогресс
        overall = (detected_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Прогресс по категориям
        categories = {}
        for category in set(m.category for m in self.markers.values()):
            cat_markers = [m for m in self.markers.values() if m.category == category]
            cat_weight = sum(m.weight for m in cat_markers)
            cat_detected = sum(
                m.weight * m.confidence 
                for m in cat_markers 
                if m.detected
            )
            categories[category] = (cat_detected / cat_weight * 100) if cat_weight > 0 else 0
        
        self.progress = {
            "overall": overall,
            "categories": categories,
            "markers_detected": self._count_detected_markers(),
            "markers_total": len(self.markers),
            "last_scan": datetime.now().isoformat()
        }
    
    def _count_detected_markers(self) -> int:
        """Подсчитать количество обнаруженных маркеров"""
        return sum(1 for m in self.markers.values() if m.detected)
    
    def _generate_portfolio(self):
        """Генерация портфолио через AI"""
        logger.info("  📝 Generating portfolio...")
        
        if not self.ai_manager.get_active_provider():
            logger.warning("AI provider not available, skipping portfolio generation")
            return
        
        # Подготовка контекста
        detected_markers = [
            {"name": m.name, "level": m.level, "confidence": m.confidence}
            for m in self.markers.values()
            if m.detected
        ]
        
        prompt = f"""
На основе обнаруженных маркеров компетенций сгенерируй портфолио:

Обнаруженные маркеры ({len(detected_markers)}):
{json.dumps(detected_markers, indent=2, ensure_ascii=False)}

Общий прогресс: {self.progress.get('overall', 0):.1f}%

Сгенерируй портфолио в формате JSON:
{{
  "summary": "Краткое описание компетенций",
  "strengths": ["Список сильных сторон"],
  "areas_for_improvement": ["Что можно улучшить"],
  "career_recommendations": ["Карьерные рекомендации"],
  "next_markers": ["Какие маркеры добавить дальше"]
}}
"""
        
        response = chat_with_fallback([
            {"role": "system", "content": "Ты — карьерный консультант и эксперт по IT."},
            {"role": "user", "content": prompt}
        ])
        
        if response:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    portfolio = json.loads(json_match.group())
                    self.progress["portfolio"] = portfolio
                    logger.info("✅ Portfolio generated")
            except:
                logger.warning("Failed to parse portfolio JSON")
    
    def _save_results(self):
        """Сохранить результаты сканирования"""
        # Создаем директории
        self.compass_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем маркеры
        markers_data = {k: asdict(v) for k, v in self.markers.items()}
        with open(self.markers_file, "w", encoding="utf-8") as f:
            json.dump(markers_data, f, indent=2, ensure_ascii=False)
        
        # Сохраняем прогресс
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
        
        # Сохраняем портфолио
        if "portfolio" in self.progress:
            with open(self.portfolio_file, "w", encoding="utf-8") as f:
                json.dump(self.progress["portfolio"], f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to {self.compass_dir}")
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """Получить карьерные рекомендации"""
        if "portfolio" not in self.progress:
            self._generate_portfolio()
        
        return self.progress.get("portfolio", {}).get("career_recommendations", [])
    
    def get_next_markers(self) -> List[Dict[str, str]]:
        """Получить список следующих маркеров для достижения"""
        if "portfolio" not in self.progress:
            self._generate_portfolio()
        
        return self.progress.get("portfolio", {}).get("next_markers", [])
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус IT Compass"""
        return {
            "project_path": str(self.project_path),
            "markers_detected": self._count_detected_markers(),
            "markers_total": len(self.markers),
            "progress": self.progress.get("overall", 0),
            "categories": self.progress.get("categories", {}),
            "last_scan": self.progress.get("last_scan"),
            "ai_provider": self.ai_manager.get_active_provider()
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
    # CLI интерфейс
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
        print(f"   Markers: {results['markers_detected']}/{results['markers_total']}")
        print(f"   Progress: {results['progress']['overall']:.1f}%")
    
    elif args.status:
        scanner = get_scanner()
        status = scanner.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()
