"""Pytest configuration for thought_architecture."""

import sys
from pathlib import Path

# Добавляем папку молекулы в путь ПЕРВОЙ
molecule_root = Path(__file__).parent.parent
if str(molecule_root) not in sys.path:
