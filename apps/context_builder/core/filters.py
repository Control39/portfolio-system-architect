import re
from pathlib import Path
from typing import List, Set
from fnmatch import fnmatch

from ..config.settings import settings


class FileFilter:
    """Фильтрация файлов при сканировании"""
    
    def __init__(self):
        self.extensions: Set[str] = set(settings.default_extensions)
        self.excluded_dirs: Set[str] = set(settings.excluded_dirs)
        self.excluded_files: Set[str] = set(settings.excluded_files)
        self.max_size_bytes: int = settings.max_file_size_mb * 1024 * 1024
    
    def add_extension(self, ext: str):
        """Добавить расширение"""
        if not ext.startswith("."):
            ext = f".{ext}"
        self.extensions.add(ext.lower())
    
    def remove_extension(self, ext: str):
        """Удалить расширение"""
        if not ext.startswith("."):
            ext = f".{ext}"
        self.extensions.discard(ext.lower())
    
    def should_include(self, file_path: Path, project_root: Path) -> bool:
        """Проверить, должен ли файл быть включён"""
        
        # Проверка размера
        if file_path.stat().st_size > self.max_size_bytes:
            return False
        
        # Проверка исключённых директорий
        try:
            rel_path = file_path.relative_to(project_root)
        except ValueError:
            return False
        
        for part in rel_path.parts:
            if part in self.excluded_dirs:
                return False
        
        # Проверка исключённых файлов (с поддержкой wildcard)
        for pattern in self.excluded_files:
            if fnmatch(file_path.name, pattern):
                return False
        
        # Проверка расширения
        if file_path.suffix.lower() not in self.extensions:
            return False
        
        return True
    
    def get_stats(self) -> dict:
        """Статистика фильтра"""
        return {
            "extensions": sorted(self.extensions),
            "excluded_dirs": sorted(self.excluded_dirs),
            "excluded_files": sorted(self.excluded_files),
            "max_file_size_mb": settings.max_file_size_mb,
        }