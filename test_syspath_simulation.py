import sys

# This simulates what conftest.py does
# After pytest.ini adds paths, conftest.py runs

# Current sys.path (after pytest.ini):
# [0]: C:\repo\apps (from pytest.ini ..)
# [1]: C:\repo (from pytest.ini ../..)
# [7]: C:\repo\apps\ai_config_manager\src (from pytest.ini .)

# conftest.py should:
# 1. Remove MOLECULE_SRC from wherever it is
# 2. Insert MOLECULE_SRC at [0]
# 3. Remove SRC_PATH from wherever it is  
# 4. Insert SRC_PATH at [0]

# Let's simulate this
sys.path = [
    "C:/repo/apps",  # [0] - from pytest.ini
    "C:/repo",       # [1] - from pytest.ini
    "C:/Users/Z/.pyenv/pyenv-win/versions/3.12.5/python312.zip",
    "C:/Users/Z/.pyenv/pyenv-win/versions/3.12.5/DLLs",
    "C:/Users/Z/.pyenv/pyenv-win/versions/3.12.5/Lib",
    "C:/Users/Z/.pyenv/pyenv-win/versions/3.12.5",
    "C:/Users/Z/.pyenv/pyenv-win/versions/3.12.5/Lib/site-packages",
    "C:/repo/apps/ai_config_manager/src",  # [7] - from pytest.ini
    "__editable__.portfolio_organizer-1.0.0.finder.__path_hook__",
    "C:/repo",  # [9] - from pytest.ini
]

print("=== BEFORE conftest.py ===")
for i, p in enumerate(sys.path[:10]):
    print(f"  [{i}]: {p}")

# Now conftest.py runs:
MOLECULE_SRC = "C:/repo/apps/ai_config_manager/src"
SRC_PATH = "C:/repo/src"

# Remove from current position if exists
if MOLECULE_SRC in sys.path:
    sys.path.remove(MOLECULE_SRC)
# Insert at front
sys.path.insert(0, MOLECULE_SRC)

if SRC_PATH in sys.path:
    sys.path.remove(SRC_PATH)
sys.path.insert(0, SRC_PATH)

print("\n=== AFTER conftest.py ===")
for i, p in enumerate(sys.path[:10]):
    print(f"  [{i}]: {p}")

# Now test import:
print("\n=== Testing import ===")
try:
    import ai_config_manager
    print(f"ai_config_manager.__file__: {ai_config_manager.__file__}")
    from ai_config_manager.config_manager import ConfigManager
    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
