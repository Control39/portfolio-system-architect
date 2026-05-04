#!/usr/bin/env python3
"""
Основной скрипт сканера проекта для Cognitive Automation Agent.
Выполняет анализ технологического стека, зависимостей и архитектуры.
Исправленная версия с защитой от циклических зависимостей и переполнения памяти.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Создание директорий для логов перед инициализацией логирования
LOG_DIR = Path("apps/cognitive-agent/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DIR / "scanner.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ProjectScanner:
    """Сканер проекта для анализа технологического стека и архитектуры"""

    def __init__(self, config_path: str = "apps/cognitive-agent/config/scanner.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.scan_results = {}
        # Защита от циклических зависимостей
        self.visited_paths = set()
        self.max_files_to_scan = 5000

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации сканера"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return {}

    def _safe_rglob(self, path: Path, pattern: str = "*", max_depth: int = 5):
        """Безопасный рекурсивный поиск с ограничением глубины"""
        ignore_dirs = {
            '.git', '.venv', 'node_modules', '__pycache__', '.cache',
            '.pytest_cache', 'venv', 'env', '.mypy_cache', '.ruff_cache',
            '.idea', '.vscode', 'dist', 'build', '.egg-info', 'htmlcov',
            '.coverage', 'reports', '.private', 'target', 'bin', 'obj'
        }
        
        def walk_dir(current_path: Path, current_depth: int, count: int):
            if current_depth > max_depth or count >= self.max_files_to_scan:
                return
            try:
                for item in current_path.iterdir():
                    if count >= self.max_files_to_scan:
                        break
                    try:
                        real_path = item.resolve()
                        if real_path in self.visited_paths:
                            continue
                        self.visited_paths.add(real_path)

                        if item.is_dir(follow_symlinks=False):
                            if item.name not in ignore_dirs and not item.name.startswith('.'):
                                yield from walk_dir(item, current_depth + 1, count)
                        else:
                            yield item
                            count += 1
                    except (PermissionError, OSError, RecursionError):
                        continue
            except (PermissionError, OSError):
                pass
        
        return walk_dir(path, 0, 0)

    def scan_project(self, project_path: str = ".") -> Dict[str, Any]:
        """Выполнение сканирования проекта"""
        logger.info(f"Начало сканирования проекта: {project_path}")

        project_path = Path(project_path)
        start_time = time.time()

        # Сбор информации о проекте
        self.scan_results = {
            "project_info": self._get_project_info(project_path),
            "tech_stack": self._analyze_tech_stack(project_path),
            "dependencies": self._analyze_dependencies(project_path),
            "scan_metadata": {
                "scan_time": time.time() - start_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        }

        # Сохранение результатов
        self._save_results()

        logger.info(f"Сканирование завершено за {time.time() - start_time:.2f} секунд")
        return self.scan_results

    def _get_project_info(self, project_path: Path) -> Dict[str, Any]:
        """Получение базовой информации о проекте"""
        logger.info("Сбор информации о проекте...")

        info = {
            "name": project_path.name,
            "path": str(project_path.absolute()),
            "git_repository": self._check_git_repository(project_path),
        }

        return info

    def _analyze_tech_stack(self, project_path: Path) -> Dict[str, Any]:
        """Анализ технологического стека"""
        logger.info("Анализ технологического стека...")

        tech_stack = {
            "languages": self._detect_languages(project_path),
            "frameworks": self._detect_frameworks(project_path),
            "databases": self._detect_databases(project_path),
            "tools": self._detect_tools(project_path),
        }

        return tech_stack

    def _analyze_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Анализ зависимостей проекта"""
        logger.info("Анализ зависимостей...")

        dependencies = {
            "python": self._get_python_dependencies(project_path),
            "nodejs": self._get_nodejs_dependencies(project_path),
            "docker": self._get_docker_dependencies(project_path),
        }

        return dependencies

    def _check_git_repository(self, path: Path) -> bool:
        """Проверка, является ли директория Git репозиторием"""
        return (path / ".git").exists()

    def _detect_languages(self, path: Path) -> List[str]:
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

        try:
            for file_path in self._safe_rglob(path, "*", 5):
                if file_path.suffix in extensions:
                    languages.add(extensions[file_path.suffix])
        except Exception as e:
            logger.warning(f"Ошибка обнаружения языков: {e}")

        return list(languages)

    def _detect_frameworks(self, path: Path) -> List[str]:
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
            try:
                if (path / file_name).exists():
                    frameworks.append(framework)
            except Exception:
                continue

        return list(set(frameworks))

    def _detect_databases(self, path: Path) -> List[str]:
        """Обнаружение баз данных"""
        databases = []
        db_files = {
            "docker-compose.yml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
            "docker-compose.yaml": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
        }

        for file_name, possible_dbs in db_files.items():
            try:
                file_path = path / file_name
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for db in possible_dbs:
                            if db.lower() in content.lower():
                                databases.append(db)
            except Exception as e:
                logger.debug(f"Ошибка чтения {file_name}: {e}")

        return list(set(databases))

    def _detect_tools(self, path: Path) -> List[str]:
        """Обнаружение инструментов"""
        tools = []

        # Проверка по характерным файлам
        tool_files = {
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker Compose",
            "docker-compose.yaml": "Docker Compose",
            "Makefile": "Make",
            "package.json": "npm/yarn",
            "pyproject.toml": "Poetry/PDM",
            "requirements.txt": "pip",
            "pom.xml": "Maven",
            "go.mod": "Go Modules",
        }

        for file_name, tool in tool_files.items():
            try:
                if (path / file_name).exists():
                    tools.append(tool)
            except Exception:
                continue

        return list(set(tools))

    def _get_python_dependencies(self, path: Path) -> List[str]:
        """Получение Python зависимостей"""
        deps = []
        req_files = ["requirements.txt", "pyproject.toml", "setup.py", "requirements-dev.txt"]

        for req_file in req_files:
            try:
                req_path = path / req_file
                if req_path.exists():
                    deps.append(f"Найден файл зависимостей: {req_file}")
            except Exception:
                continue

        return deps

    def _get_nodejs_dependencies(self, path: Path) -> List[str]:
        """Получение Node.js зависимостей"""
        deps = []
        try:
            if (path / "package.json").exists():
                deps.append("Найден package.json")
            if (path / "package-lock.json").exists():
                deps.append("Найден package-lock.json")
            if (path / "yarn.lock").exists():
                deps.append("Найден yarn.lock")
        except Exception:
            pass
        return deps

    def _get_docker_dependencies(self, path: Path) -> List[str]:
        """Получение Docker зависимостей"""
        deps = []
        try:
            if (path / "Dockerfile").exists():
                deps.append("Найден Dockerfile")
            if (path / "docker-compose.yml").exists() or (path / "docker-compose.yaml").exists():
                deps.append("Найден docker-compose файл")
        except Exception:
            pass
        return deps

    def _save_results(self):
        """Сохранение результатов сканирования"""
        reports_dir = Path("apps/cognitive-agent/reports/scans")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"scan_report_{timestamp}.json"

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(self.scan_results, f, indent=2, ensure_ascii=False)

            logger.info(f"Отчет сохранен: {report_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отчета: {e}")


def main():
    """Основная функция запуска"""
    try:
        scanner = ProjectScanner()
        results = scanner.scan_project(".")

        # Вывод краткой информации
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ ПРОЕКТА")
        print("=" * 60)

        project_info = results.get("project_info", {})
        print(f"Проект: {project_info.get('name', 'N/A')}")
        print(f"Git репозиторий: {'Да' if project_info.get('git_repository') else 'Нет'}")

        tech_stack = results.get("tech_stack", {})
        print(f"Языки: {', '.join(tech_stack.get('languages', [])) or 'Не обнаружены'}")
        print(f"Фреймворки: {', '.join(tech_stack.get('frameworks', [])) or 'Не обнаружены'}")

        scan_meta = results.get("scan_metadata", {})
        print(f"Время сканирования: {scan_meta.get('scan_time', 0):.2f} сек")

        print("=" * 60)

        # Сохранение статуса для мониторинга
        status_file = Path("apps/cognitive-agent/scans/last_scan_status.json")
        status_file.parent.mkdir(parents=True, exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "status": "success",
                    "timestamp": time.time(),
                    "scan_id": time.strftime("%Y%m%d_%H%M%S"),
                },
                f,
                indent=2,
            )

        return 0

    except Exception as e:
        logger.error(f"Ошибка при сканировании: {e}")

        # Сохранение статуса ошибки
        status_file = Path("apps/cognitive-agent/scans/last_scan_status.json")
        status_file.parent.mkdir(parents=True, exist_ok=True)

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(
                {"status": "error", "timestamp": time.time(), "error": str(e)},
                f,
                indent=2,
            )

        return 1


if __name__ == "__main__":
    sys.exit(main())
