# apps/ai_config_manager/tests/conftest.py
"""
Фикстуры и настройки для всех тестов.
Автоматически добавляет src/ в sys.path.
"""

import sys
from pathlib import Path

import pytest

# Определяем пути
REPO_ROOT = Path(__file__).resolve().parents[2]  # до /apps/ai_config_manager
SRC_PATH = REPO_ROOT / "src"

# Добавляем src в путь, если ещё не добавлен
if str(SRC_PATH) not in sys.path:


# Автоматическая очистка (опционально)
@pytest.fixture(autouse=True)
def ensure_path_cleanup():
    """Убедиться, что sys.path не засоряется."""
    old_path = sys.path.copy()
    yield
    sys.path[:] = old_path  # восстанавливаем после теста
