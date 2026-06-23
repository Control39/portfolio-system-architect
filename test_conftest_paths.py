"""Test conftest.py path additions."""

import sys
from pathlib import Path

print("=== sys.path before any changes ===")
for i, p in enumerate(sys.path[:5]):
    print(f"  [{i}]: {p}")

# Test relative paths from apps/ai_config_manager/tests/
# rootdir is C:\repo\apps\ai_config_manager when running from there

CURRENT_DIR = Path.cwd()
print(f"\n=== Current directory: {CURRENT_DIR} ===")

# From apps/ai_config_manager/tests/, the relative paths would be:
# . -> apps/ai_config_manager/tests
# ../src -> apps/ai_config_manager/src (which is correct!)
# .. -> apps/ai_config_manager
# ../.. -> C:\repo

# Simulate conftest.py being in the tests directory
CONFTEST_PATH = CURRENT_DIR / "conftest.py"
print(f"Conftest path: {CONFTEST_PATH}")

# What pytest conftest.py does:
# REPO_ROOT = Path(__file__).resolve().parents[3]  # from tests/ -> apps/ -> ai_config_manager/ -> C:\repo
# MOLECULE_SRC = Path(__file__).resolve().parents[1] / "src"  # from tests/ -> apps/ai_config_manager/src

# Actually in conftest.py:
# REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/ -> parent = apps/ai_config_manager, parents[1] = apps/, parents[2] = C:\repo, parents[3] would be C:\
# That's wrong!

# Let's calculate correctly:
# tests/ has parents: [apps/ai_config_manager, apps, C:\repo, C:\]
# parents[0] = apps/ai_config_manager
# parents[1] = apps
# parents[2] = C:\repo
# parents[3] = C:\

# So:
# REPO_ROOT = parents[2]
# MOLECULE_ROOT = parents[0]
# MOLECULE_SRC = parents[0] / "src"

print("\n=== Correct path calculation from tests/ ===")
parents = list(Path(__file__).resolve().parents)
print(f"  parents[0] (apps/ai_config_manager): {parents[0]}")
print(f"  parents[1] (apps): {parents[1]}")
print(f"  parents[2] (C:\\repo): {parents[2]}")
print(f"  parents[3] (C:\\): {parents[3]}")

REPO_ROOT = Path(__file__).resolve().parents[2]
MOLECULE_ROOT = Path(__file__).resolve().parents[0]
MOLECULE_SRC = MOLECULE_ROOT / "src"

print(f"\nREPO_ROOT: {REPO_ROOT}")
print(f"MOLECULE_SRC: {MOLECULE_SRC}")
print(f"MOLECULE_SRC exists: {MOLECULE_SRC.exists()}")

# Add paths as conftest.py would
print("\n=== Adding paths from conftest.py ===")
if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))
    print(f"Added {MOLECULE_SRC} to sys.path[0]")

print("\n=== Try to import ai_config_manager ===")
try:
    import ai_config_manager

    print(f"Success! ai_config_manager: {ai_config_manager}")
    print(f"  __file__: {ai_config_manager.__file__}")
    print(f"  __path__: {ai_config_manager.__path__}")
except Exception as e:
    print(f"Failed: {e}")
