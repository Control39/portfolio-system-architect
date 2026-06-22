from pathlib import Path

# When pytest runs:
# 1. It sets rootdir to apps/ai_config_manager (where test file is)
# 2. It processes pythonpath entries relative to rootdir

rootdir = Path("C:/repo/apps/ai_config_manager")
pythonpath_entries = ['.', '..', '../..', '../../src']

print("Relative to rootdir (C:/repo/apps/ai_config_manager):")
for entry in pythonpath_entries:
    abs_path = (rootdir / entry).resolve()
    print(f"  {entry} -> {abs_path}")

print("\nBut if paths were resolved from C:/repo (where pytest was invoked):")
for entry in pythonpath_entries:
    abs_path = (Path("C:/repo") / entry).resolve()
    print(f"  {entry} -> {abs_path}")
