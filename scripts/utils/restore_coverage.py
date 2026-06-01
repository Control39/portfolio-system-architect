#!/usr/bin/env python3
"""Restore original coverage threshold in pytest.ini."""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PYTEST_INI = REPO_ROOT / "pytest.ini"
BACKUP = PYTEST_INI.with_suffix(PYTEST_INI.suffix + ".backup")

if BACKUP.exists():
    BACKUP.rename(PYTEST_INI)
    print("✅ Restored original pytest.ini with coverage 80%")
else:
    print("⚠️ No backup found, checking manually...")
    if PYTEST_INI.exists():
        content = PYTEST_INI.read_text()
        if "cov-fail-under=50" in content:
            content = content.replace("cov-fail-under=50", "cov-fail-under=80")
            PYTEST_INI.write_text(content)
            print("✅ Manually restored coverage to 80%")
        else:
            print("✅ Coverage already at 80% or not found")
