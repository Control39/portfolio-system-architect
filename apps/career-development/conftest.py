import sys
import os
from pathlib import Path

# Автоматически добавляем папку src/ текущего сервиса в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))