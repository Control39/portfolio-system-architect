"""Debug conftest.py - run by pytest."""

import sys
from pathlib import Path

print("\n=== conftest.py DEBUG ===")
print(f"__file__: {__file__}")
print(f"cwd: {Path.cwd()}")

CONFTEST_FILE = Path(__file__).resolve()
print(f"conftest path: {CONFTEST_FILE}")
print(f"parents[0]: {CONFTEST_FILE.parents[0]}")  # tests/
print(f"parents[1]: {CONFTEST_FILE.parents[1]}")  # apps/ai_config_manager
print(f"parents[2]: {CONFTEST_FILE.parents[2]}")  # apps/
print(f"parents[3]: {CONFTEST_FILE.parents[3]}")  # C:\repo

REPO_ROOT = CONFTEST_FILE.parents[3]
SRC_PATH = REPO_ROOT / "src"
MOLECULE_SRC = CONFTEST_FILE.parents[1] / "src"

print("\nPaths to add:")
print(f"  SRC_PATH: {SRC_PATH}")
print(f"  MOLECULE_SRC: {MOLECULE_SRC}")

# Current logic from conftest.py
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
    print("Added SRC_PATH to sys.path[0]")

if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))
    print("Added MOLECULE_SRC to sys.path[0]")

print("\n=== sys.path[0:5] ===")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

# Try to import
print("\n=== Try to import ai_config_manager ===")
try:
    import ai_config_manager

    print(f"Success! ai_config_manager.__file__ = {ai_config_manager.__file__}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
