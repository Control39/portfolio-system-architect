"""Conftest that imports test_config.py to see the error."""

import sys
from pathlib import Path

# Use hardcoded path
CONFTEST_FILE = Path("C:/repo/apps/ai_config_manager/tests/conftest.py").resolve()
print(f"CONFTEST_FILE: {CONFTEST_FILE}")
print(f"parents[0]: {CONFTEST_FILE.parents[0]}")
print(f"parents[1]: {CONFTEST_FILE.parents[1]}")
print(f"parents[2]: {CONFTEST_FILE.parents[2]}")
print(f"parents[3]: {CONFTEST_FILE.parents[3]}")

REPO_ROOT = CONFTEST_FILE.parents[3]
SRC_PATH = REPO_ROOT / "src"
MOLECULE_SRC = CONFTEST_FILE.parents[1] / "src"

print(f"\nREPO_ROOT: {REPO_ROOT}")
print(f"SRC_PATH: {SRC_PATH}")
print(f"MOLECULE_SRC: {MOLECULE_SRC}")

if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

print("\n=== sys.path[0:5] ===")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

# Try to import test_config.py
print("\n=== Importing test_config.py ===")
try:
    import apps.ai_config_manager.tests.test_config as tc

    print("Success!")
    print(f"test_config module: {tc}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
