"""
Service Registry для Cognitive Agent
Предоставляет профили всех микросервисов и автоматическое определение технологий.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ServiceProfile:
    """
    Профиль микросервиса для управления стратегией тестирования и другими задачами.
    
    Содержит метаданные о сервисе, которые определяют, как с ним работать.
    """
    name: str
    path: str  # Путь к корневой папке сервиса (относительно репозитория)
    language: str = 'python'  # 'python', 'go', 'java' etc.
    framework: Optional[str] = None  # 'fastapi', 'flask', 'django', 'spring-boot' etc.
    criticality: str = 'medium'  # 'critical', 'high', 'medium', 'low'
    test_frameworks: List[str] = field(default_factory=lambda: ['pytest'])
    coverage_target: float = 80.0  # Базовая цель покрытия
    is_active: bool = True  # Активен ли сервис
    
    def get_test_dir(self) -> str:
        """Возвращает путь к директории с тестами на основе языка."""
        if self.language == 'python':
            return f"{self.path}/tests"
        elif self.language == 'go':
            return self.path  # В Go тесты рядом с кодом
        elif self.language == 'java':
            return f"{self.path}/src/test"
        else:
            return f"{self.path}/tests"
    
    def get_criticality_priority(self) -> int:
        """Возвращает приоритет критичности (меньше = выше приоритет)."""
        priorities = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return priorities.get(self.criticality, 3)


class ServiceDiscovery:
    """
    Автоматическое определение технологий сервисов по файлам.
    """
    
    # Паттерны для определения Python фреймворков
    PYTHON_FRAMEWORK_PATTERNS = {
        'fastapi': [
            r'from fastapi',
            r'import fastapi',
            r'FastAPI\(',
            r'@app\.(get|post|put|delete)\('
        ],
        'flask': [
            r'from flask',
            r'import flask',
            r'Flask\(',
            r'@app\.route'
        ],
        'django': [
            r'from django',
            r'import django',
            r'django\.setup\(',
            r'class.*\(models\.Model\)'
        ]
    }
    
    # Файлы для определения языка
    LANGUAGE_INDICATORS = {
        'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
        'go': ['go.mod', 'go.sum'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts']
    }
    
    @classmethod
    def detect_language(cls, service_path: str) -> str:
        """Определить язык программирования сервиса."""
        path = Path(service_path)
        
        for language, files in cls.LANGUAGE_INDICATORS.items():
            for file in files:
                if (path / file).exists():
                    return language
        
        return 'python'  # По умолчанию Python
    
    @classmethod
    def detect_framework(cls, service_path: str, language: str = 'python') -> Optional[str]:
        """Определить фреймворк по содержимому файлов."""
        if language != 'python':
            return None
        
        path = Path(service_path)
        
        for framework, patterns in cls.PYTHON_FRAMEWORK_PATTERNS.items():
            for py_file in path.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            return framework
                except Exception:
                    continue
        
        return 'base'  # Без фреймворка
    
    @classmethod
    def detect_criticality(cls, service_path: str) -> str:
        """Определить критичность по содержимому и расположению."""
        path = Path(service_path)
        
        # Высокая критичность для ключевых сервисов
        critical_indicators = [
            path.name in ['cognitive_agent', 'decision_engine', 'it_compass'],
            (path / 'main.py').exists(),
            (path / '__init__.py').exists()
        ]
        
        if sum(critical_indicators) >= 2:
            return 'high'
        
        return 'medium'


class ServiceRegistry:
    """
    Реестр всех микросервисов с их профилями.
    
    Поддерживает:
    - Автоматическое обнаружение сервисов
    - Загрузку профилей из конфига
    - Обновление профилей при изменении технологий
    """
    
    def __init__(self, repo_root: str = None, config_path: str = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.config_path = Path(config_path) if config_path else None
        self.profiles: Dict[str, ServiceProfile] = {}
        
        # Загрузить профили
        self._load_profiles()
    
    def _load_profiles(self):
        """Загрузить профили из конфига или автодетект."""
        # 1. Попытаться загрузить из конфига
        if self.config_path and self.config_path.exists():
            try:
                self._load_from_config()
                logger.info(f"✅ ServiceRegistry: загружено {len(self.profiles)} профилей из конфига")
                return
            except Exception as e:
                logger.warning(f"⚠️ Не удалось загрузить профили из конфига: {e}, использую автодетект")
        
        # 2. Автодетект сервисов
        self._discover_services()
        logger.info(f"✅ ServiceRegistry: обнаружено {len(self.profiles)} сервисов")
    
    def _load_from_config(self):
        """Загрузить профили из YAML-конфига."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        for service_config in config.get('services', []):
            profile = ServiceProfile(
                name=service_config['name'],
                path=service_config.get('path', f"apps/{service_config['name']}"),
                language=service_config.get('language', 'python'),
                framework=service_config.get('framework'),
                criticality=service_config.get('criticality', 'medium'),
                test_frameworks=service_config.get('test_frameworks', ['pytest']),
                coverage_target=service_config.get('coverage_target', 80.0)
            )
            self.profiles[profile.name] = profile
    
    def _discover_services(self):
        """Автоматически обнаружить все сервисы в apps/ и agents/."""
        # 1. Сканировать apps/
        apps_dir = self.repo_root / 'apps'
        if apps_dir.exists():
            for service_dir in apps_dir.iterdir():
                if service_dir.is_dir() and not service_dir.name.startswith('.'):
                    self._add_service_from_path(service_dir)
        
        # 2. Сканировать agents/
        agents_dir = self.repo_root / 'agents'
        if agents_dir.exists():
            for agent_dir in agents_dir.iterdir():
                if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
                    self._add_service_from_path(agent_dir)
    
    def _add_service_from_path(self, path: Path):
        """Добавить сервис из директории с автодетектом."""
        language = ServiceDiscovery.detect_language(str(path))
        framework = ServiceDiscovery.detect_framework(str(path), language)
        criticality = ServiceDiscovery.detect_criticality(str(path))
        
        profile = ServiceProfile(
            name=path.name,
            path=str(path.relative_to(self.repo_root)),
            language=language,
            framework=framework,
            criticality=criticality,
            test_frameworks=['pytest'] if language == 'python' else [],
            coverage_target=90.0 if criticality in ['high', 'critical'] else 80.0
        )
        self.profiles[profile.name] = profile
    
    def get_profile(self, service_name: str) -> Optional[ServiceProfile]:
        """Получить профиль по имени сервиса."""
        return self.profiles.get(service_name)
    
    def get_profile_by_path(self, file_path: str) -> Optional[ServiceProfile]:
        """
        Определить, какому сервису принадлежит файл.
        
        Args:
            file_path: Полный путь к файлу или относительный от repo_root
            
        Returns:
            ServiceProfile или None, если файл вне известных сервисов
        """
        file_path = Path(file_path)
        
        # Если абсолютный путь, сделать относительным
        if file_path.is_absolute():
            try:
                file_path = file_path.relative_to(self.repo_root)
            except ValueError:
                return None
        
        # Проверить каждый профиль
        for profile in self.profiles.values():
            profile_path = Path(profile.path)
            
            # Совпадение точное или вложенный файл
            if str(file_path) == str(profile_path) or str(file_path).startswith(str(profile_path)):
                return profile
        
        return None
    
    def get_active_profiles(self) -> List[ServiceProfile]:
        """Получить все активные профили."""
        return [p for p in self.profiles.values() if p.is_active]
    
    def get_high_priority_profiles(self) -> List[ServiceProfile]:
        """Получить профили с высокой/критичной важностью."""
        return [
            p for p in self.profiles.values() 
            if p.is_active and p.criticality in ['high', 'critical']
        ]
    
    def get_profiles_by_language(self, language: str) -> List[ServiceProfile]:
        """Получить профили по языку программирования."""
        return [p for p in self.profiles.values() if p.language == language]
    
    def get_profiles_by_framework(self, framework: str) -> List[ServiceProfile]:
        """Получить профили по фреймворку."""
        return [p for p in self.profiles.values() if p.framework == framework]
    
    def to_dict(self) -> Dict[str, dict]:
        """Преобразовать в словарь для JSON/YAML."""
        return {
            name: {
                'name': p.name,
                'path': p.path,
                'language': p.language,
                'framework': p.framework,
                'criticality': p.criticality,
                'test_frameworks': p.test_frameworks,
                'coverage_target': p.coverage_target
            }
            for name, p in self.profiles.items()
        }
