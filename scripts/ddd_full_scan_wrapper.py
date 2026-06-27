#!/usr/bin/env python3
"""ddd_full_scan_wrapper.py - Обёртка для ddd_full_scan.sh"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point"""
    # Определить корень репозитория
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    # Запустить ddd_analyzer.py напрямую
    ddd_analyzer = repo_root / "scripts" / "ddd_analyzer.py"

    if not ddd_analyzer.exists():
        print(f"❌ Файл {ddd_analyzer} не найден")
        sys.exit(1)

    # Запуск
    result = subprocess.run([sys.executable, str(ddd_analyzer), "."], cwd=str(repo_root), capture_output=False)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
