#!/usr/bin/env python3
"""
Move root files to appropriate locations.
Docs to docs/, scripts to scripts/, clean temp files.
"""

import shutil
from pathlib import Path


PROJECT_ROOT = Path("C:/repo")

# Files to move to docs/
docs_to_move = [
    "CURRENT_STATE_SUMMARY.md",
    "ORGANIZATION_COMPLETE.md",
    "CLEANUP_ROOT.md",
    "REFACTORING_DIAGNOSIS_REPORT.md",
    "REFACTORING_MOVE_PLAN.md",
    "REFACTORING_SUMMARY.md",
    "SRC_APPS_REFACTORING.md",
    "TEST_FIXES.md",
    "NOTIFY_GITHUB_GUIDE.txt",
]

# Files to move to scripts/
scripts_to_move = [
    "notify_github.py",
    "update_dependencies.py",
    "update_pipfile.py",
    "pytest_debug.py",
    "trace_pytest_paths.py",
]

# Files to delete (temp/scan files)
temp_to_delete = [
    "bandit-report-full.json",
    "bandit-report.json",
    "coverage.json",
    "vulnerabilities.json",
    "trivy-secret.yaml",
]

# Files to check (manual review needed)
check_files = [
    "conftest.py",
    "check_*.py",
    "fix_*.py",
    "find_*.py",
    "generate_*.py",
    "test_*.py",
    "debug_*.py",
    "phase2_integration_test_results.json",
    "agent-logs-*.zip",
]


def move_file(source: str, target_dir: str, new_name: str = None) -> bool:
    """Move a file and return success status."""
    source_path = PROJECT_ROOT / source
    target_path = PROJECT_ROOT / target_dir / (new_name or source)

    if not source_path.exists():
        print(f"  SKIP (not found): {source}")
        return False

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(target_path))
        print(f"  MOVED: {source} → {target_path.relative_to(PROJECT_ROOT)}")
        return True
    except Exception as e:
        print(f"  FAIL: {source} → {target_path.relative_to(PROJECT_ROOT)} ({e})")
        return False


def delete_file(filename: str) -> bool:
    """Delete a file and return success status."""
    file_path = PROJECT_ROOT / filename

    if not file_path.exists():
        print(f"  SKIP (not found): {filename}")
        return False

    try:
        file_path.unlink()
        print(f"  DELETED: {filename}")
        return True
    except Exception as e:
        print(f"  FAIL: {filename} ({e})")
        return False


def main():
    print("=" * 70)
    print("MOVE ROOT FILES TO APPROPRIATE LOCATIONS")
    print("=" * 70)

    success = 0
    fail = 0

    # 1. Create docs subdirectories
    print("\n1. Creating docs subdirectories...")
    docs_dirs = ["docs/refactoring", "docs/status", "docs/guides", "docs/security"]
    for d in docs_dirs:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d}")

    # 2. Move docs to docs/
    print("\n2. Moving documentation to docs/:")
    for doc in docs_to_move:
        if move_file(doc, "docs/refactoring"):
            success += 1
        else:
            fail += 1

    # 3. Move scripts to scripts/
    print("\n3. Moving scripts to scripts/utils/:")
    for script in scripts_to_move:
        if move_file(script, "scripts/utils"):
            success += 1
        else:
            fail += 1

    # 4. Delete temp files
    print("\n4. Deleting temporary/scan files:")
    for temp in temp_to_delete:
        if delete_file(temp):
            success += 1
        else:
            fail += 1

    # 5. Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: Success={success}, Fail={fail}")
    print("=" * 70)

    print("\nFiles requiring manual review:")
    print("  - conftest.py (pytest config)")
    print("  - check_*.py (scan scripts)")
    print("  - fix_*.py (fix scripts)")
    print("  - find_*.py (find scripts)")
    print("  - generate_*.py (generator scripts)")
    print("  - test_*.py (test scripts)")
    print("  - debug_*.py (debug scripts)")
    print("  - phase2_integration_test_results.json")
    print("  - agent-logs-*.zip")
    print("\nRecommendation: Move these to scripts/automation/ or scripts/dev/")

    print("\nNext steps:")
    print("1. Review the changes with 'git status'")
    print("2. Commit: 'git add -u && git add <moved files>'")
    print("3. Commit: 'git commit -m \"docs: move reports to docs/ && scripts: move utils to scripts/\"'")


if __name__ == "__main__":
    main()
