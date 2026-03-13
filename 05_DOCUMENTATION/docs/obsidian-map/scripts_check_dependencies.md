# Check Dependencies

- **Путь**: `scripts\check_dependencies.py`
- **Тип**: .PY
- **Размер**: 14,122 байт
- **Последнее изменение**: 2026-03-06 14:17:40

## Превью

```
#!/usr/bin/env python3
"""
Скрипт для проверки и унификации зависимостей в проекте.
Проверяет соответствие зависимостей в компонентах и корневом requirements.txt.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml

class DependencyChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.components_dir = self.project_root / "components"
        
    def find_requirements_fi
... (файл продолжается)
```
