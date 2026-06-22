# apps/ai_config_manager/tests/conftest.py
"""
Фикстуры и настройки для всех тестов.
Автоматически добавляет src/ и molecule root в sys.path.
"""

import sys
from pathlib import Path

import pytest

# Определяем пути
REPO_ROOT = Path(__file__).resolve().parents[4]  # до корня репозитория
MOLECULE_ROOT = Path(__file__).resolve().parents[1]  # до /apps/ai_config_manager
SRC_PATH = REPO_ROOT / "src"

# Добавляем корневой src в путь (для импорта общих модулей)
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Добавляем корень репозитория (для импорта apps.* модулей)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Автоматическая очистка (опционально)
@pytest.fixture(autouse=True)
def ensure_path_cleanup():
    """Убедиться, что sys.path не засоряется."""
    old_path = sys.path.copy()
    yield
    sys.path[:] = old_path  # восстанавливаем после теста
