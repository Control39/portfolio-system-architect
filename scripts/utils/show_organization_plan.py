#!/usr/bin/env python3
"""
Ultra-safe script for organizing repository - NO RECURSIVE SEARCH.
Only shows what WOULD be moved.
"""

import os
import json
from pathlib import Path
from typing import Dict


def load_dependency_map(project_root: Path) -> Dict:
    map_file = project_root / "docs" / "dev_guide" / "dependency_map.json"
    if map_file.exists():
        with open(map_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def show_plans(project_root: Path):
    """Just show what would be moved - NO ACTUAL MOVING."""
    scripts_dir = project_root / "scripts"
    tools_dir = project_root / "tools"

    print("=" * 70)
    print("REPOSITORY ORGANIZATION PLAN - NO ACTIONS PERFORMED")
    print("=" * 70)

    print("\n1. UTILITIES DIRECTORY STRUCTURE (to be created):")
    print("   utilities/")
    print("   ├── onboarding/")
    print("   │   ├── setup_env.py")
    print("   │   ├── check_dependencies.py")
    print("   │   └── first_run.py")
    print("   ├── helpers/")
    print("   │   ├── explain_error.py")
    print("   │   ├── suggest_fix.py")
    print("   │   └── glossary.py")
    print("   └── learning/")
    print("       ├── tutorial_git.py")
    print("       ├── tutorial_docker.py")
    print("       └── tutorial_testing.py")

    print("\n2. SCRIPTS REORGANIZATION:")
    print("   scripts/maintenance/ (from scripts/utils/):")
    print("       - check_status.ps1")
    print("       - quick_test.py")
    print("       - restore_coverage.py")

    print("\n   scripts/migrations/ (from scripts/migration/):")
    print("       - collect_readmes.py")
    print("       - copy_root_files.py")
    print("       - fix_imports_after_migration.py")

    print("\n   scripts/backup/ (new category):")
    print("       - search_backup.ps1")
    print("       - verify_hashes.ps1")

    print("\n3. TOOLS REORGANIZATION:")
    print("   tools/analyzers/ (from tools/):")
    print("       - check_duplicates.py")
    print("       - check_rules.py")
    print("       - check_skills.py")
    print("       - workspace_analyzer.py")

    print("\n   tools/debuggers/ (from scripts/diagnostics/):")
    print("       - health_check.py")
    print("       - complete_diagnostic.py")
    print("       - debug_pytest_config.py")

    print("\n   tools/automation/ (from scripts/automation/):")
    print("       - consolidate_adrs.py (FIXED)")
    print("       - consolidate_cases.py")
    print("       - start_dev.py")

    print("\n4. AGENT-RELATED SCRIPTS (REMAIN WHERE THEY ARE - NEED MANUAL REVIEW):")
    agent_keywords = ["agent", "gigacode", "auto", "cognitive"]
    for script in ["scripts/ai/", "scripts/automation/", "scripts/diagnostics/"]:
        print(f"   {script}:")
        script_dir = project_root / script.replace("/", "\\")
        if script_dir.exists():
            for f in script_dir.glob("*.py"):
                if any(kw in f.name.lower() for kw in agent_keywords):
                    print(f"     - {f.name}")

    print("\n5. POWERSHELL SCRIPTS TO REORGANIZE:")
    print("   Move to utilities/automation/:")
    for ps1_file in ["scripts/ai/*.ps1", "scripts/automation/*.ps1"]:
        print(f"     {ps1_file}")

    print("\n6. SHELL SCRIPTS TO REORGANIZE:")
    print("   Keep in scripts/linux/ (server-specific)")
    print("   Keep in scripts/git/ (git-specific)")
    print("   Keep in scripts/deployment/ (deployment-specific)")

    print("\n" + "=" * 70)
    print("SAFETY MEASURES:")
    print("=" * 70)
    print("✓ Agent scripts will NOT be moved (need manual review)")
    print("✓ No 'git add -A' will be executed")
    print("✓ All actions will be logged to docs/REPOSITORY_ORGANIZATION_GUIDE.md")
    print("✓ You can review changes BEFORE committing")

    print("\n" + "=" * 70)
    print("READY TO PROCEED?")
    print("=" * 70)
    print("If you approve this plan, I will:")
    print("1. Create the new directory structure")
    print("2. Move files (non-agent only)")
    print("3. Update import paths")
    print("4. Generate git commands for review")
    print("\nReply: 'PROCEED' or 'CANCEL'")


def main():
    project_root = Path("C:/repo")

    print("\nLoading dependency map...")
    dependency_map = load_dependency_map(project_root)
    print(f"Found {dependency_map.get('total_scripts', 0)} scripts in dependency map")

    show_plans(project_root)


if __name__ == "__main__":
    main()
