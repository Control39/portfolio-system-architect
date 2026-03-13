# Generate Obsidian Map

- **Путь**: `07_TOOLS\scripts\scripts\generate_obsidian_map.py`
- **Тип**: .PY
- **Размер**: 5,105 байт
- **Последнее изменение**: 2026-03-12 10:52:00

## Превью

```
"""
Генерирует Obsidian-карту знаний из структуры репозитория portfolio-system-architect.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Set

# Пути
REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
OUTPUT_DIR: Path = REPO_ROOT / "docs" / "obsidian-map"
README_PATH: Path = REPO_ROOT / "README.md"

# Игнорируемые директории (точное совпадение через set intersection)
IGNORED_DIRS: Set[str] = {
    ".git", "__pycache__", "node_modules", "venv", "env", 
 
... (файл продолжается)
```
