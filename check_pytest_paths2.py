"""Check pytest paths relative to rootdir."""
import sys
from pathlib import Path

# When pytest runs from apps/ai_config_manager/tests/, rootdir is apps/ai_config_manager
rootdir = Path("C:/repo/apps/ai_config_manager")

# pytest.ini pythonpath entries
pythonpath_entries = ['.', '..', '../..', '../../src']

print("Paths resolved from rootdir (C:/repo/apps/ai_config_manager):")
for p in pythonpath_entries:
    abs_path = (rootdir / p).resolve()
    print(f"  {p} -> {abs_path}")
