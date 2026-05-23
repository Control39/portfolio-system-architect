import shutil
from pathlib import Path

files = [
    ("CONTRIBUTING.md", "CONTRIBUTING.md"),
    ("CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("SECURITY.md", "SECURITY.md"),
]

for src, dst in files:
    if Path(src).exists():
        shutil.copy(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Source not found: {src}")
