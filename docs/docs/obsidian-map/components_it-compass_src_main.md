# Main

- **Путь**: `components\it-compass\src\main.py`
- **Тип**: .PY
- **Размер**: 7,600 байт
- **Последнее изменение**: 2026-03-06 14:43:00

## Превью

```
"""
IT Compass - система объективного отслеживания карьерного роста в IT
Основное консольное приложение
"""

import os
import sys
from core.tracker import SkillTracker
from utils.portfolio_gen import PortfolioGenerator


def show_directions(tracker):
    """Показать список направлений"""
    directions = tracker.get_directions()
    print("\n🎯 Доступные направления:")
    for i, direction in enumerate(directions, 1):
        print(f"{i}. {direction}")


def show_markers_for_direction(tracker, di
... (файл продолжается)
```

