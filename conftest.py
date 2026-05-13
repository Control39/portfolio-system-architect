"""Глобальные настройки для pytest."""

import sys
from pathlib import Path


# Добавляем корень проекта в PYTHONPATH для корректных импортов
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Добавляем apps/ для относительных импортов
APPS_DIR = ROOT_DIR / "apps"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(1, str(APPS_DIR))
