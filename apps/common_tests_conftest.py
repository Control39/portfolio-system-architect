# apps/*/tests/conftest.py
"""
Фикстуры и настройки для всех тестов микросервисов.
Автоматически добавляет корневой src/ и корень репозитория в sys.path.

Правила импортов:
1. Общие модули (src/): from src.common.health_check import health_check
2. Модули микросервиса (apps/*/src/): from apps.ai_config_manager.config_manager import ConfigManager
3. Относительные импорты внутри микросервиса: from .config_manager import ConfigManager
"""

import sys
from pathlib import Path

import pytest

# Определяем пути
REPO_ROOT = Path(__file__).resolve().parents[4]  # до корня репозитория
MOLECULE_ROOT = Path(__file__).resolve().parents[1]  # до /apps/molecule_name
SRC_PATH = REPO_ROOT / "src"

# Добавляем корневой src/ (для импорта общих модулей)
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
