import fnmatch
import logging
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config.settings import settings

logger = logging.getLogger(settings.service_name)


def normalize_path(path: str) -> str:
    """Convert Windows path to POSIX-style for internal use"""
    return str(Path(path).resolve()).replace("\\", "/")


@dataclass
class FileInfo:
    """Информация о файле"""

    path: str
    relative_path: str
    size: int
    extension: str
    is_binary: bool
    line_count: int = 0


class ProjectScanner:
    """Сканирование проекта с поддержкой .gitignore"""

    def __init__(self, project_root: Path, respect_gitignore: bool = True):
        self.project_root = Path(project_root).resolve()
        self.respect_gitignore = respect_gitignore
        self.ignored_patterns: set[str] = set()
        self.gitignore_rules: list[str] = []

        if self.respect_gitignore:
            self._load_gitignore()

    def _load_gitignore(self):
        """Загружает .gitignore файл"""
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            try:
                content = gitignore_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.gitignore_rules.append(line)
                logger.info(f"Loaded {len(self.gitignore_rules)} rules from .gitignore")
            except Exception as e:
                logger.warning(f"Could not read .gitignore: {e}")

    def _is_ignored(self, path: Path) -> bool:
        """Проверяет, должен ли файл/директория быть проигнорирован"""
        rel_path = str(path.relative_to(self.project_root))

        # Нормализуем путь для кроссплатформенной работы
        rel_path_normalized = normalize_path(rel_path)

        # Проверяем системные исключения
        if any(part.startswith(".") and part not in {".gitignore", ".env"} for part in path.parts):
            if ".git" not in rel_path:
                return True

        # Проверяем .gitignore правила
        for pattern in self.gitignore_rules:
            if pattern.endswith("/"):
                # Директория
                if fnmatch.fnmatch(rel_path_normalized + "/", pattern) or any(
                    fnmatch.fnmatch(part + "/", pattern) for part in path.parts
                ):
                    return True
            else:
                # Файл
                if fnmatch.fnmatch(rel_path_normalized, pattern) or fnmatch.fnmatch(path.name, pattern):
                    return True

        # Проверяем стандартные исключения
        if any(part in settings.exclude_dirs for part in path.parts):
            return True

        return False

    def _is_binary_file(self, file_path: Path) -> bool:
        """Определяет, является ли файл бинарным"""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(8192)
                # Проверяем наличие null-байтов
                if b"\0" in chunk:
                    return True
                # Проверяем, является ли текст валидным UTF-8
                try:
                    chunk.decode("utf-8")
                    return False
                except UnicodeDecodeError:
                    return True
        except Exception:
            return True

    def _get_extension(self, file_path: Path) -> str:
        """Возвращает расширение файла без точки"""
        ext = file_path.suffix.lower()
        return ext[1:] if ext else ""

    def _count_lines(self, file_path: Path) -> int:
        """Подсчитывает количество строк в файле"""
        try:
            with open(file_path, encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def scan(self, subpath: str = None) -> Generator[FileInfo, None, None]:
        """Сканирует проект и возвращает информацию о файлах"""
        scan_root = self.project_root
        if subpath:
            scan_root = self.project_root / subpath
            if not scan_root.exists():
                raise FileNotFoundError(f"Path not found: {subpath}")

        for file_path in scan_root.rglob("*"):
            if not file_path.is_file():
                continue

            # Пропускаем игнорируемые файлы
            if self._is_ignored(file_path):
                continue

            # Проверяем размер
            size = file_path.stat().st_size
            if size > settings.max_file_size_mb * 1024 * 1024:
                logger.debug(f"Skipping large file: {file_path} ({size} bytes)")
                continue

            # Проверяем расширение
            ext = self._get_extension(file_path)
            if ext and ext not in settings.include_extensions:
                continue

            rel_path = str(file_path.relative_to(self.project_root))
            is_binary = self._is_binary_file(file_path)

            file_info = FileInfo(
                path=normalize_path(str(file_path)),
                relative_path=normalize_path(rel_path),
                size=size,
                extension=ext,
                is_binary=is_binary,
            )

            if not is_binary:
                file_info.line_count = self._count_lines(file_path)

            yield file_info

    def get_structure_only(self, subpath: str = None) -> dict[str, Any]:
        """Возвращает только структуру директорий и файлов"""
        structure = {}
        scan_root = self.project_root
        if subpath:
            scan_root = self.project_root / subpath
            if not scan_root.exists():
                raise FileNotFoundError(f"Path not found: {subpath}")

        for file_path in sorted(scan_root.rglob("*")):
            if self._is_ignored(file_path):
                continue

            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts

            current = structure
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    if file_path.is_file():
                        ext = self._get_extension(file_path)
                        if ext and ext in settings.include_extensions:
                            current[part] = {"type": "file", "size": file_path.stat().st_size, "extension": ext}
                else:
                    if part not in current:
                        current[part] = {"type": "dir", "children": {}}
                    current = current[part]["children"]

        return structure

    def get_stats(self) -> dict[str, Any]:
        """Возвращает статистику по проекту"""
        files_count = 0
        total_size = 0
        binary_count = 0
        text_count = 0
        extensions = {}

        for file_info in self.scan():
            files_count += 1
            total_size += file_info.size
            if file_info.is_binary:
                binary_count += 1
            else:
                text_count += 1

            if file_info.extension:
                extensions[file_info.extension] = extensions.get(file_info.extension, 0) + 1

        return {
            "files_count": files_count,
            "total_size_mb": total_size / (1024 * 1024),
            "binary_files": binary_count,
            "text_files": text_count,
            "extensions": extensions,
        }
