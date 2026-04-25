#!/usr/bin/env python3
"""Основной скрипт сканера проекта для Cognitive Automation Agent.
Выполняет анализ технологического стека, зависимостей и архитектуры.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(".agents/logs/scanner.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

class ProjectScanner:
    """Сканер проекта для анализа технологического стека и архитектуры"""

    def __init__(self, config_path: str = ".agents/config/scanner.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.scan_results = {}

    def _load_config(self) -> dict[str, Any]:
        """Загрузка конфигурации сканера"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}

    def scan_project(self, project_path: str = ".") -> dict[str, Any]:
        """Выполнение сканирования проекта"""
        logger.info(f"Начало сканирования проекта: {project_path}")

        project_path = Path(project_path)
        start_time = time.time()

        # Сбор информации о проекте
        self.scan_results = {
            "project_info": self._get_project_info(project_path),
            "tech_stack": self._analyze_tech_stack(project_path),
            "dependencies": self._analyze_dependencies(project_path),
            "architecture": self._analyze_architecture(project_path),
            "security": self._analyze_security(project_path),
            "quality": self._analyze_code_quality(project_path),
            "performance": self._analyze_performance(project_path),
            "scan_metadata": {
                "scan_time": time.time() - start_time,
                "files_scanned": self._count_files(project_path),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        }

        # Сохранение результатов
        self._save_results()

        logger.info(f"Сканирование завершено за {time.time() - start_time:.2f} секунд")
        return self.scan_results

    def _get_project_info(self, project_path: Path) -> dict[str, Any]:
        """Получение базовой информации о проекте"""
        logger.info("Сбор информации о проекте...")

        info = {
            "name": project_path.name,
            "path": str(project_path.absolute()),
            "size_mb": self._get_directory_size(project_path) / (1024 * 1024),
            "file_count": self._count_files(project_path),
            "directory_count": self._count_directories(project_path),
            "git_repository": self._check_git_repository(project_path),
            "creation_time": self._get_creation_time(project_path),
            "modification_time": self._get_modification_time(project_path),
        }

        return info

    def _analyze_tech_stack(self, project_path: Path) -> dict[str, Any]:
        """Анализ технологического стека"""
        logger.info("Анализ технологического стека...")

        tech_stack = {
            "languages": self._detect_languages(project_path),
            "frameworks": self._detect_frameworks(project_path),
            "databases": self._detect_databases(project_path),
            "tools": self._detect_tools(project_path),
            "build_systems": self._detect_build_systems(project_path),
            "ci_cd": self._detect_ci_cd(project_path),
        }

        return tech_stack

    def _analyze_dependencies(self, project_path: Path) -> dict[str, Any]:
        """Анализ зависимостей проекта"""
        logger.info("Анализ зависимостей...")

        dependencies = {
            "python": self._get_python_dependencies(project_path),
            "nodejs": self._get_nodejs_dependencies(project_path),
            "java": self._get_java_dependencies(project_path),
            "dotnet": self._get_dotnet_dependencies(project_path),
            "docker": self._get_docker_dependencies(project_path),
            "external_apis": self._get_external_apis(project_path),
        }

        return dependencies

    def _analyze_architecture(self, project_path: Path) -> dict[str, Any]:
        """Анализ архитектурных паттернов"""
        logger.info("Анализ архитектурных паттернов...")

        architecture = {
            "patterns": self._detect_architectural_patterns(project_path),
            "modules": self._identify_modules(project_path),
            "interfaces": self._identify_interfaces(project_path),
            "data_flow": self._analyze_data_flow(project_path),
            "communication_patterns": self._detect_communication_patterns(project_path),
        }

        return architecture

    def _analyze_security(self, project_path: Path) -> dict[str, Any]:
        """Анализ безопасности"""
        logger.info("Анализ безопасности...")

        security = {
            "vulnerabilities": self._check_vulnerabilities(project_path),
            "secrets": self._check_hardcoded_secrets(project_path),
            "permissions": self._check_permissions(project_path),
            "encryption": self._check_encryption(project_path),
            "authentication": self._check_authentication(project_path),
        }

        return security

    def _analyze_code_quality(self, project_path: Path) -> dict[str, Any]:
        """Анализ качества кода"""
        logger.info("Анализ качества кода...")

        quality = {
            "complexity": self._calculate_complexity(project_path),
            "duplication": self._check_duplication(project_path),
            "test_coverage": self._check_test_coverage(project_path),
            "documentation": self._check_documentation(project_path),
            "code_smells": self._detect_code_smells(project_path),
        }

        return quality

    def _analyze_performance(self, project_path: Path) -> dict[str, Any]:
        """Анализ производительности"""
        logger.info("Анализ производительности...")

        performance = {
            "bottlenecks": self._identify_bottlenecks(project_path),
            "memory_usage": self._estimate_memory_usage(project_path),
            "response_time": self._estimate_response_time(project_path),
            "scalability": self._assess_scalability(project_path),
            "caching": self._check_caching(project_path),
        }

        return performance

    # Вспомогательные методы (заглушки для демонстрации)

    def _get_directory_size(self, path: Path) -> float:
        """Получение размера директории"""
        total_size = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    def _count_files(self, path: Path) -> int:
        """Подсчет файлов в директории"""
        return sum(1 for _ in path.rglob("*") if _.is_file())

    def _count_directories(self, path: Path) -> int:
        """Подсчет директорий"""
        return sum(1 for _ in path.rglob("*") if _.is_dir())

    def _check_git_repository(self, path: Path) -> bool:
        """Проверка, является ли директория Git репозиторием"""
        return (path / ".git").exists()

    def _get_creation_time(self, path: Path) -> str | None:
        """Получение времени создания"""
        try:
            return time.ctime(path.stat().st_ctime)
        except:
            return None

    def _get_modification_time(self, path: Path) -> str | None:
        """Получение времени последнего изменения"""
        try:
            return time.ctime(path.stat().st_mtime)
        except:
            return None

    def _detect_languages(self, path: Path) -> list[str]:
        """Обнаружение языков программирования"""
        languages = set()
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
        }

        for file_path in path.rglob("*"):
            if file_path.suffix in extensions:
                languages.add(extensions[file_path.suffix])

        return list(languages)

    def _detect_frameworks(self, path: Path) -> list[str]:
        """Обнаружение фреймворков"""
        frameworks = []

        # Проверка по характерным файлам
        framework_files = {
            "requirements.txt": "Python",
            "package.json": "Node.js",
            "pom.xml": "Java/Spring",
            "build.gradle": "Java/Gradle",
            "docker-compose.yml": "Docker",
            "docker-compose.yaml": "Docker",
        }

        for file_name, framework in framework_files.items():
            if (path / file_name).exists():
                frameworks.append(framework)

        return frameworks

    def _detect_databases(self, path: Path) -> list[str]:
        """Обнаружение баз данных"""
        databases = []
        db_files = {
            "docker-compose.yml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.yaml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.override.yml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.override.yaml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.prod.yml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.prod.yaml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
        }

        for file_name, possible_dbs in db_files.items():
            file_path = path / file_name
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        for db in possible_dbs:
                            if db.lower() in content.lower():
                                databases.append(db)
                except:
                    pass

        # Проверка конфигурационных файлов
        config_patterns = {
            "postgresql": ["postgres", "pg", "postgresql"],
            "mysql": ["mysql", "mariadb"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "sqlite": ["sqlite"],
            "elasticsearch": ["elasticsearch", "es"],
        }

        for config_file in path.rglob("*.yml"):
            if config_file.is_file():
                try:
                    with open(config_file, encoding="utf-8") as f:
                        content = f.read().lower()
                        for db, keywords in config_patterns.items():
                            if any(keyword in content for keyword in keywords):
                                if db.capitalize() not in databases:
                                    databases.append(db.capitalize())
                except:
                    continue

        return list(set(databases))

    def _detect_tools(self, path: Path) -> list[str]:
        """Обнаружение инструментов"""
        tools = []

        # Проверка по характерным файлам
        tool_files = {
            ".github/workflows/": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            "Jenkinsfile": "Jenkins",
            "docker-compose.yml": "Docker Compose",
            "docker-compose.yaml": "Docker Compose",
            "Dockerfile": "Docker",
            "Makefile": "Make",
            "package.json": "npm/yarn",
            "pyproject.toml": "Poetry/PDM",
            "requirements.txt": "pip",
            "pom.xml": "Maven",
            "build.gradle": "Gradle",
            "Cargo.toml": "Cargo",
            "go.mod": "Go Modules",
        }

        for file_pattern, tool in tool_files.items():
            if "*" in file_pattern:
                # Паттерн с wildcard
                for file_path in path.rglob(file_pattern.replace("*", "")):
                    if file_path.is_file():
                        tools.append(tool)
                        break
            elif (path / file_pattern).exists():
                tools.append(tool)

        return list(set(tools))

    def _detect_build_systems(self, path: Path) -> list[str]:
        """Обнаружение систем сборки"""
        build_systems = []

        build_files = {
            "Makefile": "Make",
            "CMakeLists.txt": "CMake",
            "meson.build": "Meson",
            "build.gradle": "Gradle",
            "pom.xml": "Maven",
            "package.json": "npm/yarn",
            "pyproject.toml": "Poetry/PDM",
            "setup.py": "setuptools",
            "Cargo.toml": "Cargo",
            "go.mod": "Go build",
        }

        for file_name, build_system in build_files.items():
            if (path / file_name).exists():
                build_systems.append(build_system)

        return build_systems

    def _detect_ci_cd(self, path: Path) -> list[str]:
        """Обнаружение CI/CD систем"""
        ci_cd_systems = []

        ci_files = {
            ".github/workflows/": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            "Jenkinsfile": "Jenkins",
            ".travis.yml": "Travis CI",
            "circleci/config.yml": "CircleCI",
            "azure-pipelines.yml": "Azure Pipelines",
            ".drone.yml": "Drone CI",
            "bitbucket-pipelines.yml": "Bitbucket Pipelines",
        }

        for file_pattern, ci_system in ci_files.items():
            if file_pattern.endswith("/"):
                # Директория
                if (path / file_pattern).exists():
                    ci_cd_systems.append(ci_system)
            elif (path / file_pattern).exists():
                ci_cd_systems.append(ci_system)

        return ci_cd_systems

    def _get_python_dependencies(self, path: Path) -> list[str]:
        """Получение Python зависимостей"""
        deps = []
        req_files = ["requirements.txt", "pyproject.toml", "setup.py"]

        for req_file in req_files:
            req_path = path / req_file
            if req_path.exists():
                deps.append(f"Найден файл зависимостей: {req_file}")

        return deps

    def _get_nodejs_dependencies(self, path: Path) -> list[str]:
        """Получение Node.js зависимостей"""
        deps = []
        if (path / "package.json").exists():
            deps.append("Найден package.json")
        if (path / "package-lock.json").exists():
            deps.append("Найден package-lock.json")
        if (path / "yarn.lock").exists():
            deps.append("Найден yarn.lock")
        return deps

    def _get_java_dependencies(self, path: Path) -> list[str]:
        """Получение Java зависимостей"""
        deps = []
        if (path / "pom.xml").exists():
            deps.append("Найден pom.xml (Maven)")
        if (path / "build.gradle").exists():
            deps.append("Найден build.gradle (Gradle)")
        return deps

    def _get_dotnet_dependencies(self, path: Path) -> list[str]:
        """Получение .NET зависимостей"""
        deps = []
        if (path / "*.csproj").exists():
            deps.append("Найден .csproj файл")
        if (path / "*.sln").exists():
            deps.append("Найден .sln файл")
        return deps

    def _get_docker_dependencies(self, path: Path) -> list[str]:
        """Получение Docker зависимостей"""
        deps = []
        if (path / "Dockerfile").exists():
            deps.append("Найден Dockerfile")
        if (path / "docker-compose.yml").exists() or (path / "docker-compose.yaml").exists():
            deps.append("Найден docker-compose файл")
        return deps

    def _get_external_apis(self, path: Path) -> list[str]:
        """Получение информации о внешних API"""
        apis = []

        # Поиск упоминаний API в конфигурационных файлах
        api_keywords = ["api", "endpoint", "url", "base_url", "service", "client"]
        config_extensions = [".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".conf"]

        for config_file in path.rglob("*"):
            if config_file.suffix in config_extensions and config_file.is_file():
                try:
                    with open(config_file, encoding="utf-8") as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in api_keywords):
                            apis.append(f"Конфигурационный файл: {config_file.name}")
                except:
                    continue

        return apis

    def _identify_modules(self, path: Path) -> list[str]:
        """Идентификация модулей"""
        modules = []

        # Поиск директорий с исходным кодом
        src_dirs = ["src", "lib", "app", "apps", "modules", "components", "services"]
        for src_dir in src_dirs:
            src_path = path / src_dir
            if src_path.exists() and src_path.is_dir():
                modules.append(f"Директория исходного кода: {src_dir}")

        # Поиск Python модулей
        for py_file in path.rglob("*.py"):
            if py_file.name == "__init__.py":
                module_dir = py_file.parent
                if module_dir != path:
                    modules.append(f"Python модуль: {module_dir.relative_to(path)}")

        return modules

    def _identify_interfaces(self, path: Path) -> list[str]:
        """Идентификация интерфейсов"""
        interfaces = []

        # Поиск файлов с интерфейсами
        interface_patterns = ["interface", "api", "contract", "schema", "protocol"]

        for file_path in path.rglob("*"):
            if file_path.is_file():
                file_name_lower = file_path.name.lower()
                if any(pattern in file_name_lower for pattern in interface_patterns):
                    interfaces.append(f"Файл интерфейса: {file_path.relative_to(path)}")

        return interfaces

    def _analyze_data_flow(self, path: Path) -> dict[str, Any]:
        """Анализ потока данных"""
        return {
            "data_sources": ["База данных", "Внешние API", "Файловая система"],
            "data_processors": ["Сервисы обработки", "Фоновые задачи"],
            "data_sinks": ["База данных", "Кэш", "Внешние системы"],
            "data_validation": "Базовая валидация присутствует",
            "data_transformation": "Преобразования данных в сервисах",
        }

    def _detect_communication_patterns(self, path: Path) -> list[str]:
        """Обнаружение паттернов коммуникации"""
        patterns = []

        # Проверка по характерным файлам и директориям
        if (path / "events").exists():
            patterns.append("Event-Driven")
        if (path / "messages").exists():
            patterns.append("Message-Based")
        if (path / "queues").exists():
            patterns.append("Queue-Based")
        if (path / "pubsub").exists():
            patterns.append("Pub/Sub")

        # Проверка конфигурационных файлов
        config_files = list(path.rglob("*.yml")) + list(path.rglob("*.yaml"))
        for config_file in config_files:
            try:
                with open(config_file, encoding="utf-8") as f:
                    content = f.read().lower()
                    if "rabbitmq" in content or "kafka" in content:
                        patterns.append("Message Broker")
                    if "grpc" in content:
                        patterns.append("gRPC")
                    if "rest" in content or "http" in content:
                        patterns.append("REST API")
            except:
                continue

        return list(set(patterns))

    def _check_hardcoded_secrets(self, path: Path) -> list[str]:
        """Проверка захардкоженных секретов"""
        secrets = []

        # Ключевые слова для поиска секретов
        secret_keywords = ["password", "secret", "token", "key", "credential", "auth"]

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read().lower()
                        for keyword in secret_keywords:
                            if keyword in content:
                                secrets.append(f"Возможный секрет в {file_path.relative_to(path)}: содержит '{keyword}'")
                                break
                except:
                    continue

        return secrets[:10]  # Ограничиваем количество для производительности

    def _check_permissions(self, path: Path) -> list[str]:
        """Проверка прав доступа"""
        permissions = []

        # Проверка Dockerfile на наличие проблем с правами
        for dockerfile in path.rglob("Dockerfile*"):
            if dockerfile.is_file():
                try:
                    with open(dockerfile, encoding="utf-8") as f:
                        content = f.read()
                        if "chmod 777" in content or "chmod a+rwx" in content:
                            permissions.append(f"Опасные права в {dockerfile.relative_to(path)}: 777")
                        if "USER root" in content and "USER nonroot" not in content:
                            permissions.append(f"Запуск от root в {dockerfile.relative_to(path)}")
                except:
                    continue

        return permissions

    def _check_encryption(self, path: Path) -> list[str]:
        """Проверка шифрования"""
        encryption = []

        # Поиск упоминаний шифрования
        encryption_keywords = ["encrypt", "decrypt", "cipher", "aes", "rsa", "ssl", "tls"]

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in encryption_keywords):
                            encryption.append(f"Шифрование в {file_path.relative_to(path)}")
                except:
                    continue

        return encryption

    def _check_authentication(self, path: Path) -> list[str]:
        """Проверка аутентификации"""
        auth = []

        # Поиск упоминаний аутентификации
        auth_keywords = ["auth", "authenticate", "login", "jwt", "oauth", "session"]

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in auth_keywords):
                            auth.append(f"Аутентификация в {file_path.relative_to(path)}")
                except:
                    continue

        return auth

    def _check_duplication(self, path: Path) -> dict[str, Any]:
        """Проверка дублирования кода"""
        return {
            "estimated_duplication": "low",
            "duplicated_files": [],
            "duplication_percentage": "0-5%",
        }

    def _check_test_coverage(self, path: Path) -> dict[str, Any]:
        """Проверка покрытия тестами"""
        return {
            "test_files_count": len(list(path.rglob("test_*.py"))) + len(list(path.rglob("*_test.py"))),
            "coverage_estimated": "medium",
            "test_framework": "pytest" if (path / "pytest.ini").exists() else "unittest",
        }

    def _check_documentation(self, path: Path) -> dict[str, Any]:
        """Проверка документации"""
        doc_files = list(path.rglob("README*")) + list(path.rglob("*.md"))
        return {
            "documentation_files": len(doc_files),
            "has_readme": any("readme" in f.name.lower() for f in doc_files),
            "documentation_quality": "good" if len(doc_files) > 5 else "basic",
        }

    def _detect_code_smells(self, path: Path) -> list[str]:
        """Обнаружение 'запахов' кода"""
        smells = []

        # Простая эвристика для демонстрации
        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        lines = f.readlines()
                        if len(lines) > 500:
                            smells.append(f"Слишком длинный файл: {file_path.relative_to(path)} ({len(lines)} строк)")
                        # Проверка на длинные функции (более 50 строк)
                        function_lines = 0
                        for line in lines:
                            if line.strip().startswith("def "):
                                if function_lines > 50:
                                    smells.append(f"Длинная функция в {file_path.relative_to(path)}: {function_lines} строк")
                                function_lines = 0
                            elif line.strip() and not line.strip().startswith("#"):
                                function_lines += 1
                except:
                    continue

        return smells[:10]

    def _identify_bottlenecks(self, path: Path) -> list[str]:
        """Идентификация узких мест"""
        bottlenecks = []

        # Поиск потенциальных узких мест
        bottleneck_patterns = [
            ("sleep(", "Использование sleep()"),
            ("time.sleep", "Использование time.sleep()"),
            ("SELECT *", "SELECT * в SQL запросах"),
            ("N+1", "Потенциальная проблема N+1"),
            ("loop", "Вложенные циклы"),
        ]

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        for pattern, description in bottleneck_patterns:
                            if pattern in content:
                                bottlenecks.append(f"{description} в {file_path.relative_to(path)}")
                except:
                    continue

        return bottlenecks[:10]

    def _estimate_memory_usage(self, path: Path) -> dict[str, Any]:
        """Оценка использования памяти"""
        return {
            "estimated_memory_usage": "medium",
            "memory_intensive_operations": ["Обработка изображений", "Работа с большими данными"],
            "optimization_recommendations": ["Использовать генераторы", "Кэшировать результаты"],
        }

    def _estimate_response_time(self, path: Path) -> dict[str, Any]:
        """Оценка времени отклика"""
        return {
            "estimated_response_time": "fast",
            "potential_bottlenecks": ["Внешние API вызовы", "Сложные запросы к БД"],
            "optimization_suggestions": ["Асинхронная обработка", "Кэширование"],
        }

    def _assess_scalability(self, path: Path) -> dict[str, Any]:
        """Оценка масштабируемости"""
        return {
            "scalability": "good",
            "horizontal_scaling": "поддерживается",
            "vertical_scaling": "поддерживается",
            "stateless": "частично",
            "recommendations": ["Добавить балансировку нагрузки", "Использовать кэш"],
        }

    def _check_caching(self, path: Path) -> list[str]:
        """Проверка кэширования"""
        caching = []

        # Поиск упоминаний кэширования
        cache_keywords = ["cache", "redis", "memcached", "lru", "ttl"]

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in cache_keywords):
                            caching.append(f"Кэширование в {file_path.relative_to(path)}")
                except:
                    continue

        return caching

    def _detect_architectural_patterns(self, path: Path) -> list[str]:
        """Обнаружение архитектурных паттернов"""
        patterns = []

        # Простая эвристика для демонстрации
        if (path / "src" / "controllers").exists():
            patterns.append("MVC")
        if (path / "services").exists():
            patterns.append("Service Layer")
        if (path / "events").exists():
            patterns.append("Event-Driven")

        return patterns

    def _check_vulnerabilities(self, path: Path) -> list[str]:
        """Проверка уязвимостей"""
        # Заглушка для демонстрации
        return ["Проверка уязвимостей требует установки дополнительных инструментов"]

    def _calculate_complexity(self, path: Path) -> dict[str, Any]:
        """Расчет сложности кода"""
        return {
            "estimated_cyclomatic_complexity": "medium",
            "cognitive_complexity": "low",
            "maintainability_index": "high",
        }

    def _save_results(self):
        """Сохранение результатов сканирования"""
        reports_dir = Path(".agents/reports/scans")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"scan_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Отчет сохранен: {report_file}")

def main():
    """Основная функция запуска сканера"""
    try:
        scanner = ProjectScanner()
        results = scanner.scan_project(".")

        # Вывод краткой информации
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ ПРОЕКТА")
        print("="*60)

        project_info = results.get("project_info", {})
        print(f"Проект: {project_info.get('name', 'N/A')}")
        print(f"Размер: {project_info.get('size_mb', 0):.2f} MB")
        print(f"Файлов: {project_info.get('file_count', 0)}")

        tech_stack = results.get("tech_stack", {})
        print(f"Языки: {', '.join(tech_stack.get('languages', []))}")
        print(f"Фреймворки: {', '.join(tech_stack.get('frameworks', []))}")

        scan_meta = results.get("scan_metadata", {})
        print(f"Время сканирования: {scan_meta.get('scan_time', 0):.2f} сек")

        print("="*60)

        # Сохранение статуса для мониторинга
        status_file = Path(".agents/scans/last_scan_status.json")
        status_file.parent.mkdir(exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump({
                "status": "success",
                "timestamp": time.time(),
                "scan_id": timestamp if "timestamp" in locals() else time.strftime("%Y%m%d_%H%M%S"),
            }, f, indent=2)

        return 0

    except Exception as e:
        logger.error(f"Ошибка при сканировании: {e}")

        # Сохранение статуса ошибки
        status_file = Path(".agents/scans/last_scan_status.json")
        status_file.parent.mkdir(exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump({
                "status": "error",
                "timestamp": time.time(),
                "error": str(e),
            }, f, indent=2)

        return 1

if __name__ == "__main__":
    sys.exit(main())
