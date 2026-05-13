import sys
from pathlib import Path


# Добавляем parent директорию для корректных импортов
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Создаем псевдо-пакет для ml-model-registry (дефисы не допустимы в Python)
import importlib.util


spec = importlib.util.spec_from_file_location("ml_model_registry", Path(__file__).parent.parent / "src" / "__init__.py")
