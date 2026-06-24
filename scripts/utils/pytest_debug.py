import pytest

print("pytest version:", pytest.__version__)

# Check what paths pytest adds
from pathlib import Path

rootdir = Path("C:/repo/apps/ai_config_manager")
print("rootdir:", rootdir)

# Relative paths from pytest.ini
paths = [".", "../src", "..", "../.."]
for p in paths:
    abs_path = (rootdir / p).resolve()
    print(f"{p} -> {abs_path} (exists: {abs_path.exists()})")
