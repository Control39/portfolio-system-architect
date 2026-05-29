from pathlib import Path
from typing import Optional
import pathspec


class GitIgnoreFilter:
    """Фильтр на основе .gitignore"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.spec = self._load_gitignore()
    
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            return None
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                return pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, 
                    f
                )
        except Exception:
            return None
    
    def is_ignored(self, file_path: Path) -> bool:
        if self.spec is None:
            return False
        
        try:
            rel_path = file_path.relative_to(self.project_root)
            return self.spec.match_file(str(rel_path))
        except ValueError:
            return False