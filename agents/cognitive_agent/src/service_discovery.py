"""
Service Discovery для Cognitive Agent
Содержит утилиты для автоматического определения технологий сервисов.
"""

import re
from pathlib import Path
from typing import Optional, Dict, List


class ServiceDiscovery:
    """
    Автоматическое определение технологий сервисов по файлам.
    
    Используется ServiceRegistry для создания профилей сервисов.
    """
    
    # Паттерны для определения Python фреймворков
    PYTHON_FRAMEWORK_PATTERNS: Dict[str, List[str]] = {
        'fastapi': [
            r'from fastapi',
            r'import fastapi',
            r'FastAPI\(',
            r'@app\.(get|post|put|delete)\(',
            r'APIRouter\(',
            r'@router\.(get|post|put|delete)\('
        ],
        'flask': [
            r'from flask',
            r'import flask',
            r'Flask\(',
            r'@app\.route',
            r'@app\.errorhandler',
            r'request\.'
        ],
        'django': [
            r'from django',
            r'import django',
            r'django\.setup\(',
            r'class.*\(models\.Model\)',
            r'class.*\(views\..*View\)',
            r'urlpatterns'
        ],
        'base': [  # Базовый Python без фреймворка
            r'if __name__ == "__main__":',
            r'def main\('
        ]
    }
    
    # Файлы для определения языка
    LANGUAGE_INDICATORS: Dict[str, List[str]] = {
        'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', '.python-version'],
        'go': ['go.mod', 'go.sum', 'main.go'],
        'java': ['pom.xml', 'build.gradle', 'build.gradle.kts', 'App.java'],
        'javascript': ['package.json', 'package-lock.json', 'index.js', 'index.ts'],
        'typescript': ['tsconfig.json', 'tsconfig.node.json']
    }
    
    # Файлы для определения критичности
    CRITICALITY_INDICATORS = {
        'critical': [
            'cognitive_agent',
            'decision_engine',
            'it_compass',
            'auth_service',
            'payment'
        ]
    }
    
    @classmethod
    def detect_language(cls, service_path: str) -> str:
        """
        Определить язык программирования сервиса по файлам конфигурации.
        
        Args:
            service_path: Путь к корневой папке сервиса
            
        Returns:
            Название языка ('python', 'go', 'java', 'javascript', 'typescript')
        """
        path = Path(service_path)
        
        for language, files in cls.LANGUAGE_INDICATORS.items():
            for file in files:
                if (path / file).exists():
                    return language
        
        # Если файлов конфигурации нет, проверить расширения файлов
        py_files = list(path.rglob('*.py'))
        js_files = list(path.rglob('*.js'))
        ts_files = list(path.rglob('*.ts'))
        go_files = list(path.rglob('*.go'))
        java_files = list(path.rglob('*.java'))
        
        if py_files and not js_files and not ts_files:
            return 'python'
        elif js_files and not py_files:
            return 'javascript'
        elif ts_files and not py_files:
            return 'typescript'
        elif go_files and not py_files:
            return 'go'
        elif java_files and not py_files:
            return 'java'
        
        return 'python'  # По умолчанию Python
    
    @classmethod
    def detect_framework(cls, service_path: str, language: str = 'python') -> Optional[str]:
        """
        Определить фреймворк по содержимому файлов.
        
        Args:
            service_path: Путь к корневой папке сервиса
            language: Язык программирования
            
        Returns:
            Название фреймворка ('fastapi', 'flask', 'django', 'base', etc.) или None
        """
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
        
        return 'base'  # Без фреймворка или базовый Python
    
    @classmethod
    def detect_criticality(cls, service_path: str) -> str:
        """
        Определить критичность сервиса по названию и содержимому.
        
        Args:
            service_path: Путь к корневой папке сервиса
            
        Returns:
            Критичность ('critical', 'high', 'medium', 'low')
        """
        path = Path(service_path)
        service_name = path.name
        
        # Высокая критичность для ключевых сервисов
        critical_names = cls.CRITICALITY_INDICATORS.get('critical', [])
        if any(name in service_name.lower() for name in critical_names):
            return 'critical'
        
        # Проверить наличие признаков высокой критичности
        high_criticality_indicators = [
            (path / 'main.py').exists(),
            (path / '__init__.py').exists(),
            (path / 'config').exists(),
            len(list(path.rglob('*.py'))) > 10  # Больше 10 файлов
        ]
        
        if sum(high_criticality_indicators) >= 2:
            return 'high'
        
        return 'medium'
    
    @classmethod
    def get_service_files(cls, service_path: str, extension: str = '.py') -> List[Path]:
        """
        Получить список всех файлов заданного расширения в сервисе.
        
        Args:
            service_path: Путь к корневой папке сервиса
            extension: Расширение файлов ('.py', '.js', '.ts', etc.)
            
        Returns:
            Список путей к файлам
        """
        path = Path(service_path)
        return list(path.rglob(f'*{extension}'))
    
    @classmethod
    def get_imports(cls, file_path: str) -> List[str]:
        """
        Получить список импортов из Python файла.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Список импортированных модулей/пакетов
        """
        path = Path(file_path)
        imports = []
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            
            # Импорт: import module
            import_pattern = r'^import\s+([\w\.]+)'
            # Импорт: from module import ...
            from_pattern = r'^from\s+([\w\.]+)\s+import'
            
            for line in content.split('\n'):
                # Пропустить комментарии
                line = line.strip()
                if line.startswith('#'):
                    continue
                
                # Импорт: import module
                match = re.match(import_pattern, line)
                if match:
                    imports.append(match.group(1).split('.')[0])
                    continue
                
                # Импорт: from module import ...
                match = re.match(from_pattern, line)
                if match:
                    imports.append(match.group(1).split('.')[0])
        except Exception:
            pass
        
        return imports
