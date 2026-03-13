# Portfolio Gen

- **Путь**: `02_MODULES\it-compass\src\utils\portfolio_gen.py`
- **Тип**: .PY
- **Размер**: 21,845 байт
- **Последнее изменение**: 2026-03-05 05:17:34

## Превью

```
"""
Генератор портфолио для IT Compass
Утилита для автоматической генерации профессионального портфолио
на основе прогресса пользователя
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader


class PortfolioGenerator:
    """Генератор профессионального портфолио"""
    
    def __init__(self, template_dir: str = "templates", output_dir: str = "portfolio"):
        """
        Инициализация 
... (файл продолжается)
```
