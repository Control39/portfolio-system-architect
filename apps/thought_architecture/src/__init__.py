"""Thought Architecture package."""
from pathlib import Path
import sys

# Добавляем текущую папку в путь
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
