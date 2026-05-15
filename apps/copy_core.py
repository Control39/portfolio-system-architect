import shutil
import sys
from pathlib import Path


src = Path(__file__).parent / "decision-engine" / "core"
dst = Path(__file__).parent / "decision_engine" / "core"

if src.exists():
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"Copied {src} -> {dst}")
else:
    print(f"Source not found: {src}")
    sys.exit(1)
