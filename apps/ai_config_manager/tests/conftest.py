# apps/ai_config_manager/tests/conftest.py
"""
Фикстуры и настройки для всех тестов.
Автоматически добавляет src/ и molecule src в sys.path.
"""

import sys
from pathlib import Path

import pytest

print("\n### conftest.py LOADED! ###", file=sys.stderr)

# Определяем пути (абсолютные, чтобы работать из любого места)
CONFTEST_FILE = Path(__file__).resolve()
REPO_ROOT = CONFTEST_FILE.parents[3]  # from tests/ -> apps/ -> ai_config_manager/ -> C:\repo
SRC_PATH = REPO_ROOT / "src"
MOLECULE_ROOT = CONFTEST_FILE.parents[1]  # apps/ai_config_manager
MOLECULE_SRC = MOLECULE_ROOT / "src"  # apps/ai_config_manager/src

# Удаляем все пути, которые могут interfere с правильным импортом
# Важно: MOLECULE_SRC должен быть ДО apps/, иначе Python найдет apps/ai_config_manager/__init__.py

# Сначала удаляем MOLECULE_SRC если он есть
mole_str = str(MOLECULE_SRC)
if mole_str in sys.path:
    sys.path.remove(mole_str)

# Удаляем REPO_ROOT / apps если он есть (чтобы избежать конфликта)
apps_str = str(REPO_ROOT / "apps")
if apps_str in sys.path:
    sys.path.remove(apps_str)

# Удаляем apps/ai_config_manager если он есть (чтобы Python не нашел apps/ai_config_manager/__init__.py)
molecule_str = str(MOLECULE_ROOT)
if molecule_str in sys.path:
    sys.path.remove(molecule_str)

# Добавляем src конкретного микросервиса ПЕРВЫМ (для импорта ai_config_manager.* модулей)
sys.path.insert(0, mole_str)

# Добавляем корневой src (для импорта общих модулей)
src_str = str(SRC_PATH)
if src_str in sys.path:
    sys.path.remove(src_str)
sys.path.insert(0, src_str)

# Добавляем корень репозитория
root_str = str(REPO_ROOT)
if root_str not in sys.path:
    sys.path.append(root_str)

print("### conftest.py DONE ###", file=sys.stderr)
print(f"sys.path[0:3] = {sys.path[0:3]}", file=sys.stderr)

# DEBUG: Проверка импорта
try:
    import ai_config_manager

    print(f"DEBUG: ai_config_manager.__file__ = {ai_config_manager.__file__}", file=sys.stderr)
    from ai_config_manager.config_manager import ConfigManager

    print(f"DEBUG: ConfigManager = {ConfigManager}", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Import error: {e}", file=sys.stderr)


# Автоматическая очистка (опционально)
@pytest.fixture(autouse=True)
def ensure_path_cleanup():
    """Убедиться, что sys.path не засоряется."""
    old_path = sys.path.copy()
    yield
    sys.path[:] = old_path  # восстанавливаем после теста
