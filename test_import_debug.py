"""Debug import."""

import sys
from pathlib import Path

# Add MOLECULE_SRC as conftest.py does
MOLECULE_SRC = Path("C:/repo/apps/ai_config_manager/src")
if str(MOLECULE_SRC) not in sys.path:
    sys.path.insert(0, str(MOLECULE_SRC))

print("sys.path[0]:", sys.path[0])
print("MOLECULE_SRC exists:", MOLECULE_SRC.exists())
print("Contents:")
for f in MOLECULE_SRC.iterdir():
    print(f"  {f.name}")

print("\nTrying to import ai_config_manager.config_manager:")
try:
    import ai_config_manager.config_manager

    print(f"Success! config_manager.__file__ = {ai_config_manager.config_manager.__file__}")
except Exception as e:
    print(f"Failed: {e}")
    import traceback

    traceback.print_exc()
