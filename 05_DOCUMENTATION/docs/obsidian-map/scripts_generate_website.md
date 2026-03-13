# Generate Website

- **Путь**: `scripts\generate_website.py`
- **Тип**: .PY
- **Размер**: 7,687 байт
- **Последнее изменение**: 2026-03-12 09:09:22

## Превью

```
"""
Генерирует профессиональный сайт-портфолио с поддержкой Mermaid и Git-статуса.
"""

import subprocess
from pathlib import Path
import markdown as md
from typing import List, Tuple, Dict

# Пути
REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
OUTPUT_DIR: Path = REPO_ROOT / "docs" / "website"
LOGO_PATH: str = REPO_ROOT / "assets" / "logo.svg"

# Игнорируемые директории
IGNORED_DIRS = {".git", "__pycache__", "node_modules", "venv", "env", 
                ".vscode", ".idea", "docs/webs
... (файл продолжается)
```
