# test_import.py
import sys
from pathlib import Path

# Добавляем корень репозитория в путь
sys.path.insert(0, str(Path(__file__).parent))

# Импорт
from src.shared.constants import APP_NAME

print(f"✅ Успех! APP_NAME = {APP_NAME}")
