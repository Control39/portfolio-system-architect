#!/usr/bin/env python3
"""
Analyze root directory structure and create organization plan.
"""

from pathlib import Path
from typing import Dict, List
import json

PROJECT_ROOT = Path("C:/repo")


def analyze_root():
    """Analyze all files and directories in the root."""

    print("=" * 70)
    print("ROOT DIRECTORY ANALYSIS")
    print("=" * 70)

    items = []

    # Get all items in root
    for item in PROJECT_ROOT.iterdir():
        if item.name.startswith("."):
            continue  # Skip hidden files/dirs (config files)

        item_type = "dir" if item.is_dir() else "file"
        items.append({"name": item.name, "type": item_type, "path": str(item.relative_to(PROJECT_ROOT))})

    # Sort by type then name
    items.sort(key=lambda x: (x["type"] == "file", x["name"]))

    print("\n1. FILES AND DIRECTORIES IN ROOT:")
    for item in items:
        print(f"  {item['type'].upper():5} - {item['name']}")

    # Categorize files
    print("\n2. CATEGORIZATION PLAN:")

    # Keep in root (standard files)
    keep_in_root = [
        "README.md",
        "LICENSE",
        "COPYING",
        "NOTICE",
        "CHANGELOG.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "CONTRIBUTING.md",
        "ARCHITECTURE.md",
        "pyproject.toml",
        "requirements.txt",
        "Pipfile",
        "Makefile",
        "Justfile",
        "Taskfile.yml",
        ".pre-commit-config.yaml",
        ".gitignore",
        ".editorconfig",
    ]

    # Move to docs/
    move_to_docs = [
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

    # Script files in root (should go to scripts/)
    script_files = [
        "notify_github.py",
        "update_dependencies.py",
        "update_pipfile.py",
        "conftest.py",
        "pytest_debug.py",
        "trace_pytest_paths.py",
    ]

    # Temp/Scan files (should be removed or moved to .gitignore)
    temp_files = ["bandit-report-full.json", "coverage.json", "vulnerabilities.json", "trivy-secret.yaml"]

    print("\n  FILES TO KEEP IN ROOT:")
    for f in keep_in_root:
        if (PROJECT_ROOT / f).exists():
            print(f"    ✓ {f}")

    print("\n  FILES TO MOVE TO docs/:")
    for f in move_to_docs:
        if (PROJECT_ROOT / f).exists():
            print(f"    → {f} → docs/refactoring/ or docs/status/")

    print("\n  SCRIPT FILES IN ROOT (move to scripts/):")
    for f in script_files:
        if (PROJECT_ROOT / f).exists():
            print(f"    → {f} → scripts/utils/ or scripts/dev/")

    print("\n  TEMP/SCAN FILES (remove or gitignore):")
    for f in temp_files:
        if (PROJECT_ROOT / f).exists():
            print(f"    ⚠ {f} - delete or ignore")

    # Directories analysis
    print("\n3. DIRECTORIES ANALYSIS:")

    dirs_to_check = ["scripts", "tools", "agents", "apps", "config", "deployment"]
    for d in dirs_to_check:
        dir_path = PROJECT_ROOT / d
        if dir_path.exists() and dir_path.is_dir():
            # Count files
            py_files = list(dir_path.rglob("*.py"))
            md_files = list(dir_path.rglob("*.md"))
            print(f"  {d}/:")
            print(f"    Python files: {len(py_files)}")
            print(f"    Markdown files: {len(md_files)}")

            # List subdirs
            subdirs = [x.name for x in dir_path.iterdir() if x.is_dir()]
            if subdirs:
                print(f"    Subdirectories: {', '.join(subdirs[:5])}")
                if len(subdirs) > 5:
                    print(f"    ... and {len(subdirs) - 5} more")

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    print("\n1. DOCS IN ROOT (move to docs/):")
    print("   - Refactoring reports → docs/refactoring/")
    print("   - Status summaries → docs/status/")
    print("   - Guides → docs/guides/")

    print("\n2. SCRIPTS IN ROOT (move to scripts/):")
    print("   - update_dependencies.py → scripts/utils/")
    print("   - update_pipfile.py → scripts/utils/")
    print("   - notify_github.py → scripts/utils/")
    print("   - conftest.py → tests/ or keep in root if pytest needs it")

    print("\n3. TEMP FILES (remove):")
    print("   - bandit-report-full.json - delete (generated)")
    print("   - coverage.json - delete (generated)")
    print("   - vulnerabilities.json - delete (generated)")
    print("   - trivy-secret.yaml - delete or move to .gitignore")

    print("\n4. AGENT-RELATED (check):")
    print("   - agents/ - review contents")
    print("   - apps/ - review contents")
    print("   - config/ - verify structure")

    print("\n" + "=" * 70)
    print("READY FOR ACTION")
    print("=" * 70)
    print("Run the appropriate script to:")
    print("1. Move docs to docs/")
    print("2. Move scripts to scripts/")
    print("3. Clean temp files")


if __name__ == "__main__":
    analyze_root()
