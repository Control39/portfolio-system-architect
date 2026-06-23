"""
Базовый сканер проекта для Cognitive Agent
"""

import hashlib
import os
import re
from collections import defaultdict
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pathspec

from .base_security import BaseSecurityChecker
from .cache_manager import MemoryAwareCache
from .exceptions import DataProcessingError, FileOperationError, ResourceExhaustionError, ValidationError
from .utils import calculate_file_hash


class BaseProjectScanner:
    """
    Базовый класс сканера проекта для Cognitive Agent
    Обеспечивает функциональность сканирования файлов и определения технологического стека
    """

    def __init__(self, project_path: str, security_checker: BaseSecurityChecker | None = None):
        """
        Инициализировать сканер проекта

        Args:
            project_path: Путь к проекту
            security_checker: Проверяльщик безопасности (опционально)
        """
        try:
            self.project_path = Path(project_path).resolve()
            if not self.project_path.exists():
                raise ValidationError(
                    f"Путь проекта не существует: {project_path}", details={"project_path": project_path}
                )
        except Exception as e:
            raise ValidationError(
                f"Ошибка инициализации сканера проекта: {str(e)}", details={"project_path": project_path}
            )

        self.security_checker = security_checker or BaseSecurityChecker()
        self.gitignore_spec = self._load_gitignore()

        # Кэш для оптимизации
        self._file_cache = MemoryAwareCache(max_size=10 * 1024 * 1024, max_items=100)  # 10MB для кэша файлов

        # Поддерживаемые расширения файлов
        self.supported_extensions = {
            "code": [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".php", ".rb"],
            "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".properties"],
            "docs": [".md", ".rst", ".txt", ".html", ".css"],
            "data": [".csv", ".json", ".xml", ".yaml", ".yml"],
        }

        # Определение технологий
        self.tech_indicators = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
                "extensions": [".py"],
                "patterns": [r"import.*django", r"import.*flask", r"import.*fastapi", r"import.*requests"],
            },
            "javascript": {
                "files": ["package.json", "yarn.lock", "package-lock.json"],
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "patterns": [r'"dependencies"', r'"devDependencies"'],
            },
            "java": {
                "files": ["pom.xml", "build.gradle", "gradle.properties"],
                "extensions": [".java"],
                "patterns": [r"import.*java\.", r"import.*javax\."],
            },
            "go": {"files": ["go.mod", "go.sum"], "extensions": [".go"], "patterns": [r"package\s+\w+", r'import\s+"']},
        }

    def _load_gitignore(self) -> pathspec.PathSpec:
        """
        Загрузить правила .gitignore

        Returns:
            PathSpec объект с правилами gitignore
        """
        try:
            gitignore_path = self.project_path / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path, encoding="utf-8") as f:
                    return pathspec.PathSpec.from_lines("gitwildmatch", f.readlines())
            return pathspec.PathSpec([])
        except Exception as e:
            raise FileOperationError(
                f"Ошибка загрузки .gitignore: {str(e)}", details={"gitignore_path": str(gitignore_path)}
            )

    def is_excluded_by_gitignore(self, file_path: Path) -> bool:
        """
        Проверить, исключен ли файл правилами .gitignore

        Args:
            file_path: Путь к файлу

        Returns:
            Исключен ли файл
        """
        try:
            relative_path = file_path.relative_to(self.project_path)
            return self.gitignore_spec.match_file(str(relative_path))
        except ValueError:
            # Если файл не находится в проекте
            return True
        except Exception as e:
            raise ValidationError(
                f"Ошибка проверки .gitignore для файла {file_path}: {str(e)}", details={"file_path": str(file_path)}
            )

    def scan(self, mode: str = "auto") -> dict[str, Any]:
        """
        Сканировать проект

        Args:
            mode: Режим сканирования ('auto', 'full', 'changed')

        Returns:
            Результаты сканирования
        """
        results = {
            "project_path": str(self.project_path),
            "files": [],
            "directories": [],
            "issues": [],
            "tech_stack": {},
            "statistics": {},
        }

        try:
            # Сканировать файлы и директории
            file_count = 0
            for root, dirs, files in os.walk(self.project_path):
                root_path = Path(root)

                # Пропустить исключенные директории
                if self.is_excluded_by_gitignore(root_path):
                    dirs.clear()  # Не заходить в поддиректории
                    continue

                results["directories"].append(str(root_path))

                for file in files:
                    file_path = root_path / file
                    relative_path = file_path.relative_to(self.project_path)

                    # Пропустить файлы, исключенные .gitignore
                    if self.is_excluded_by_gitignore(file_path):
                        continue

                    # Проверить безопасность пути
                    is_safe, message = self.security_checker.validate_path(str(file_path))
                    if not is_safe:
                        results["issues"].append(
                            {"type": "security_violation", "path": str(file_path), "message": message}
                        )
                        continue

                    # Получить информацию о файле
                    try:
                        stat = file_path.stat()
                        file_info = {
                            "path": str(relative_path),
                            "absolute_path": str(file_path),
                            "size": stat.st_size,
                            "extension": file_path.suffix.lower(),
                            "modified": stat.st_mtime,
                        }

                        # Проверить на проблемы
                        issues = self._check_file_issues(file_info)
                        results["issues"].extend(issues)

                        results["files"].append(file_info)
                        file_count += 1

                        # Проверить лимит файлов для предотвращения исчерпания ресурсов
                        if file_count > 10000:  # Пример лимита
                            raise ResourceExhaustionError(
                                "Слишком много файлов для сканирования",
                                details={"file_count": file_count, "project_path": str(self.project_path)},
                            )

                    except OSError as e:
                        results["issues"].append(
                            {
                                "type": "access_error",
                                "path": str(file_path),
                                "message": f"Ошибка доступа к файлу: {str(e)}",
                            }
                        )
        except ResourceExhaustionError:
            # Пробросить исключение исчерпания ресурсов
            raise
        except Exception as e:
            raise DataProcessingError(
                f"Ошибка сканирования проекта: {str(e)}", details={"mode": mode, "project_path": str(self.project_path)}
            )

        # Определить технологический стек
        try:
            results["tech_stack"] = self._detect_technologies(results["files"])
        except Exception as e:
            results["issues"].append(
                {"type": "tech_detection_error", "message": f"Ошибка определения технологий: {str(e)}"}
            )

        # Подсчитать статистику
        try:
            results["statistics"] = self._calculate_statistics(results["files"], results["directories"])
        except Exception as e:
            results["issues"].append(
                {"type": "stats_calculation_error", "message": f"Ошибка подсчета статистики: {str(e)}"}
            )

        return results

    def _check_file_issues(self, file_info: dict[str, Any]) -> list[dict[str, str]]:
        """
        Проверить файл на наличие проблем

        Args:
            file_info: Информация о файле

        Returns:
            Список проблем
        """
        issues = []

        # Проверить на большой размер файла (>10MB)
        if file_info["size"] > 10 * 1024 * 1024:  # 10MB
            issues.append(
                {"type": "large_file", "path": file_info["path"], "message": f"Большой файл: {file_info['size']} байт"}
            )

        # Проверить на наличие TODO комментариев (только для кодовых файлов)
        if file_info["extension"] in self.supported_extensions["code"]:
            try:
                # Использовать генератор для обработки больших файлов
                content_generator = self._read_file_in_chunks(file_info["absolute_path"])

                # Найти TODO комментарии
                for chunk in content_generator:
                    todo_matches = re.findall(r"(TODO|FIXME|HACK):\s*(.+)", chunk, re.IGNORECASE)
                    for match in todo_matches:
                        issues.append(
                            {
                                "type": "todo_comment",
                                "path": file_info["path"],
                                "message": f"TODO комментарий найден: {match[1].strip()}",
                            }
                        )
            except Exception as e:
                issues.append(
                    {"type": "read_error", "path": file_info["path"], "message": f"Ошибка чтения файла: {str(e)}"}
                )

        return issues

    def _read_file_in_chunks(self, file_path: str, chunk_size: int = 8192) -> Generator[str, None, None]:
        """
        Читать файл по частям для экономии памяти

        Args:
            file_path: Путь к файлу
            chunk_size: Размер части в байтах

        Yields:
            Части содержимого файла
        """
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except Exception:
            # Если не удалось открыть файл, вернуть пустой генератор
            return

    def _detect_technologies(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Определить технологический стек проекта

        Args:
            files: Список файлов проекта

        Returns:
            Обнаруженные технологии
        """
        tech_stack = {}

        # Сначала проверяем наличие характерных файлов
        file_names = [Path(f["path"]).name for f in files]

        for tech, indicators in self.tech_indicators.items():
            detected = False

            # Проверить наличие характерных файлов
            for indicator_file in indicators["files"]:
                if indicator_file in file_names:
                    detected = True
                    break

            # Если характерные файлы не найдены, проверить расширения
            if not detected:
                extensions = [f["extension"] for f in files]
                for indicator_ext in indicators["extensions"]:
                    if indicator_ext in extensions:
                        detected = True
                        break

            # Если ни файлы, ни расширения не помогли, проверить паттерны в содержимом
            if not detected:
                for f in files:
                    if f["extension"] in indicators["extensions"]:
                        try:
                            # Использовать генератор для обработки больших файлов
                            content_generator = self._read_file_in_chunks(f["absolute_path"])

                            for chunk in content_generator:
                                for pattern in indicators["patterns"]:
                                    if re.search(pattern, chunk, re.IGNORECASE):
                                        detected = True
                                        break
                                if detected:
                                    break
                            if detected:
                                break
                        except:
                            continue

            if detected:
                tech_stack[tech] = {
                    "confidence": "high"
                    if any(indicator in file_names for indicator in indicators["files"])
                    else "medium",
                    "files": [f["path"] for f in files if Path(f["path"]).name in indicators["files"]],
                    "extensions": list(
                        set(f["extension"] for f in files if f["extension"] in indicators["extensions"])
                    ),
                }

        return tech_stack

    def _calculate_statistics(self, files: list[dict[str, Any]], directories: list[str]) -> dict[str, Any]:
        """
        Подсчитать статистику проекта

        Args:
            files: Список файлов
            directories: Список директорий

        Returns:
            Статистика проекта
        """
        stats = {
            "total_files": len(files),
            "total_directories": len(directories),
            "total_size": sum(f["size"] for f in files),
            "file_types": defaultdict(int),
            "largest_file": None,
            "avg_file_size": 0,
        }

        # Подсчитать типы файлов
        for f in files:
            stats["file_types"][f["extension"]] += 1

        # Найти самый большой файл
        if files:
            largest = max(files, key=lambda x: x["size"])
            stats["largest_file"] = {"path": largest["path"], "size": largest["size"]}
            stats["avg_file_size"] = stats["total_size"] / len(files)

        return stats

    def get_changed_files(self, since_commit: str = "HEAD~1") -> list[str]:
        """
        Получить список измененных файлов с указанного коммита

        Args:
            since_commit: Коммит, с которого проверять изменения

        Returns:
            Список измененных файлов
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "diff", "--name-only", since_commit],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = [line.strip() for line in result.stdout.split("\n") if line.strip()]

            # Применить фильтрацию .gitignore и проверки безопасности
            filtered_files = []
            for file_path in changed_files:
                abs_path = self.project_path / file_path
                if not self.is_excluded_by_gitignore(abs_path):
                    try:
                        is_safe, _ = self.security_checker.validate_path(str(abs_path))
                        if is_safe:
                            filtered_files.append(file_path)
                    except Exception as e:
                        continue

            return filtered_files
        except subprocess.CalledProcessError as e:
            raise FileOperationError(
                f"Ошибка получения измененных файлов: {str(e)}",
                details={"since_commit": since_commit, "project_path": str(self.project_path)},
            )
        except Exception as e:
            raise FileOperationError(
                f"Неизвестная ошибка получения измененных файлов: {str(e)}",
                details={"since_commit": since_commit, "project_path": str(self.project_path)},
            )

    def calculate_project_hash(self) -> str:
        """
        Вычислить хэш проекта на основе хэшей файлов

        Returns:
            SHA256 хэш проекта
        """
        try:
            hashes = []
            for root, dirs, files in os.walk(self.project_path):
                root_path = Path(root)

                # Пропустить исключенные директории
                if self.is_excluded_by_gitignore(root_path):
                    dirs.clear()
                    continue

                for file in files:
                    file_path = root_path / file

                    # Пропустить файлы, исключенные .gitignore
                    if self.is_excluded_by_gitignore(file_path):
                        continue

                    try:
                        file_hash = calculate_file_hash(file_path)
                        hashes.append(file_hash)
                    except (FileNotFoundError, PermissionError) as e:
                        raise FileOperationError(
                            f"Ошибка чтения файла при вычислении хэша: {str(e)}",
                            details={"file_path": str(file_path)}
                        ) from e

            # Сортируем хэши для детерминированности
            hashes.sort()

            # Объединяем и вычисляем финальный хэш
            combined = "".join(hashes).encode("utf-8")
            return hashlib.sha256(combined).hexdigest()
        except Exception as e:
            raise DataProcessingError(
                f"Ошибка вычисления хэша проекта: {str(e)}", details={"project_path": str(self.project_path)}
            )

    def scan_large_files_efficiently(
        self, size_threshold: int = 10 * 1024 * 1024
    ) -> Generator[dict[str, Any], None, None]:
        """
        Эффективно сканировать большие файлы с использованием генераторов

        Args:
            size_threshold: Порог размера файла для отнесения к большим

        Yields:
            Информация о больших файлах
        """
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)

            # Пропустить исключенные директории
            if self.is_excluded_by_gitignore(root_path):
                dirs.clear()
                continue

            for file in files:
                file_path = root_path / file

                # Пропустить файлы, исключенные .gitignore
                if self.is_excluded_by_gitignore(file_path):
                    continue

                try:
                    stat = file_path.stat()
                    if stat.st_size > size_threshold:
                        yield {
                            "path": str(file_path.relative_to(self.project_path)),
                            "absolute_path": str(file_path),
                            "size": stat.st_size,
                            "extension": file_path.suffix.lower(),
                            "modified": stat.st_mtime,
                        }
                except OSError as e:
                    continue
                except Exception as e:
                    continue
