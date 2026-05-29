from pathlib import Path
from typing import List, Generator, Optional
from dataclasses import dataclass
from datetime import datetime

from .filters import FileFilter
from .gitignore_filter import GitIgnoreFilter
from .binary_detector import is_binary_file
from ..config.settings import settings


@dataclass
class FileInfo:
    """Информация о файле"""
    path: Path
    rel_path: str
    size: int
    lines: int
    extension: str
    modified: datetime
    content: Optional[str] = None


class ProjectScanner:
    """Сканер проекта"""
    
    def __init__(self, project_root: Path, respect_gitignore: bool = True):
        self.project_root = Path(project_root).resolve()
        self.filter = FileFilter()
        self.gitignore_filter = GitIgnoreFilter(self.project_root) if respect_gitignore else None
        self.respect_gitignore = respect_gitignore
    
    def scan(self, subpath: Optional[str] = None) -> Generator[FileInfo, None, None]:
        """Сканирование проекта"""
        
        scan_path = self.project_root
        if subpath:
            scan_path = self.project_root / subpath
        
        if not scan_path.exists():
            raise FileNotFoundError(f"Path not found: {scan_path}")
        
        total_size = 0
        total_files = 0
        max_total_bytes = settings.max_total_size_mb * 1024 * 1024
        
        for file_path in scan_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            if not self.filter.should_include(file_path, self.project_root):
                continue
            
            # Проверка .gitignore
            if self.gitignore_filter and self.gitignore_filter.is_ignored(file_path):
                print(f"⚠️ Пропущен (.gitignore): {file_path.relative_to(self.project_root)}")
                continue
            
            # Проверка на бинарность
            if settings.detect_binary and is_binary_file(file_path):
                print(f"⚠️ Пропущен (бинарный): {file_path.relative_to(self.project_root)}")
                continue
            
            # Проверка общего лимита
            file_size = file_path.stat().st_size
            if total_size + file_size > max_total_bytes:
                print(f"⚠️ Достигнут лимит размера, пропускаем: {file_path.relative_to(self.project_root)}")
                continue
            
            total_size += file_size
            total_files += 1
            
            if total_files > settings.max_files:
                print(f"⚠️ Достигнут лимит файлов ({settings.max_files})")
                break
            
            # Подсчёт строк
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
            except Exception:
                lines = 0
            
            yield FileInfo(
                path=file_path,
                rel_path=str(file_path.relative_to(self.project_root)),
                size=file_size,
                lines=lines,
                extension=file_path.suffix.lower(),
                modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
    
    def get_structure_only(self, subpath: Optional[str] = None) -> List[str]:
        """Только структура проекта"""
        return [info.rel_path for info in self.scan(subpath)]