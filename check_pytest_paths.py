# Check what paths pytest.ini adds
from pathlib import Path

rootdir = Path("C:/repo/apps/ai_config_manager")
paths = ['.', '../src', '..', '../..', '../../src']

print("pytest.ini pythonpath (relative to rootdir):")
for p in paths:
    abs_path = (rootdir / p).resolve()
    print(f"  {p} -> {abs_path}")
