"""Test conftest.py path additions - proper version."""

import sys
from pathlib import Path

# Simulate conftest.py in apps/ai_config_manager/tests/
# Use a hardcoded path since __file__ would be the test script itself
CONFTEST_FILE = Path("C:/repo/apps/ai_config_manager/tests/conftest.py").resolve()

print(f"Simulating conftest.py at: {CONFTEST_FILE}")
print(f"Current dir: {Path.cwd()}")

# What conftest.py calculates:
REPO_ROOT = CONFTEST_FILE.resolve().parents[3]  # from tests/ to repo root
MOLECULE_SRC = CONFTEST_FILE.resolve().parents[1] / "src"  # from tests/ to apps/*/src

print(f"\nREPO_ROOT: {REPO_ROOT}")
print(f"MOLECULE_SRC: {MOLECULE_SRC}")

# Add paths
print("\n=== Adding paths ===")
if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))
    print(f"Added {MOLECULE_SRC} to sys.path[0]")

print("\n=== sys.path[0:5] ===")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

# Try to import
print("\n=== Try to import ai_config_manager ===")
try:
    import ai_config_manager

    print(f"Success! ai_config_manager.__file__ = {ai_config_manager.__file__}")
    from ai_config_manager import ConfigManager

    print(f"ConfigManager: {ConfigManager}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
