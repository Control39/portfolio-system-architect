import sys
from pathlib import Path

# Добавляем parent директорию для корректных импортов
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
