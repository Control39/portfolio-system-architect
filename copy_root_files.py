import shutil
from pathlib import Path

files = [
    ("docs/CONTRIBUTING.md", "CONTRIBUTING.md"),
    ("docs/CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.md"),
    ("docs/CHANGELOG.md", "CHANGELOG.md"),
    ("docs/SECURITY.md", "SECURITY.md"),
]

for src, dst in files:
    if Path(src).exists():
        shutil.copy(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Source not found: {src}")
