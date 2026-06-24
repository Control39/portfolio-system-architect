#!/usr/bin/env python3
"""
Minimal repository organization - just move files, NO recursive search.
"""

import shutil
from pathlib import Path


PROJECT_ROOT = Path("C:/repo")

# Define movements
moves = [
    ("scripts/utils/check_status.ps1", "scripts/maintenance/check_status.ps1"),
    ("scripts/utils/quick_test.py", "scripts/maintenance/quick_test.py"),
    ("scripts/utils/restore_coverage.py", "scripts/maintenance/restore_coverage.py"),
    ("scripts/search_backup.ps1", "scripts/backup/search_backup.ps1"),
    ("scripts/verify_hashes.ps1", "scripts/backup/verify_hashes.ps1"),
    ("tools/check_duplicates.py", "tools/analyzers/check_duplicates.py"),
    ("tools/check_rules.py", "tools/analyzers/check_rules.py"),
    ("tools/check_skills.py", "tools/analyzers/check_skills.py"),
    ("tools/check_skills_duplicates.py", "tools/analyzers/check_skills_duplicates.py"),
    ("tools/check_teacher_duplicates.py", "tools/analyzers/check_teacher_duplicates.py"),
    ("tools/workspace_analyzer.py", "tools/analyzers/workspace_analyzer.py"),
    ("scripts/diagnostics/health_check.py", "tools/debuggers/health_check.py"),
    ("scripts/diagnostics/complete_diagnostic.py", "tools/debuggers/complete_diagnostic.py"),
    ("scripts/diagnostics/debug_pytest_config.py", "tools/debuggers/debug_pytest_config.py"),
    ("scripts/automation/consolidate_adrs.py", "tools/automation/consolidate_adrs.py"),
    ("scripts/automation/consolidate_cases.py", "tools/automation/consolidate_cases.py"),
    ("scripts/automation/start_dev.py", "tools/automation/start_dev.py"),
]

print("=" * 60)
print("MINIMAL ORGANIZATION - MOVING FILES")
print("=" * 60)

# Create directories
print("\n1. Creating directories...")
dirs = [
    "utilities/onboarding",
    "utilities/helpers",
    "utilities/learning",
    "scripts/maintenance",
    "scripts/migrations",
    "scripts/backup",
    "tools/analyzers",
    "tools/debuggers",
    "tools/automation",
]
for d in dirs:
    (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
    print(f"  Created: {d}")

# Move files
print("\n2. Moving files...")
success = 0
fail = 0

for src, tgt in moves:
    source = PROJECT_ROOT / src
    target = PROJECT_ROOT / tgt

    if not source.exists():
        print(f"  SKIP (not found): {src}")
        continue

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        print(f"  MOVED: {src} -> {tgt}")
        success += 1
    except Exception as e:
        print(f"  FAIL: {src} -> {tgt} ({e})")
        fail += 1

print("\n" + "=" * 60)
print(f"SUCCESS: {success}, FAIL: {fail}")
print("=" * 60)
print("\nNext steps:")
print("1. git status")
print("2. git add -u")
print("3. git add <new dirs>")
print("4. git commit -m 'organize: ...'")
print("5. git push")
