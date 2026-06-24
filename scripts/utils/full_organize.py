#!/usr/bin/env python3
"""
Full repository organization script with automatic import/path updates.
Safe version - only moves non-agent files and updates all references.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


# Configuration
PROJECT_ROOT = Path("C:/repo")


def update_imports_in_file(file_path: Path, old_path: str, new_path: str) -> bool:
    """Update import statements in a file. Returns True if modified."""
    try:
        content = file_path.read_text(encoding="utf-8")
        old_import = old_path.replace("\\", "/").replace(".py", "").replace("/", ".")
        new_import = new_path.replace("\\", "/").replace(".py", "").replace("/", ".")

        old_rel = old_path.replace("\\", "/")
        new_rel = new_path.replace("\\", "/")

        # Update relative imports
        new_content = re.sub(r"from\s+" + re.escape(old_import) + r"\s+import", f"from {new_import} import", content)

        # Update absolute imports
        new_content = re.sub(r"import\s+" + re.escape(old_import) + r"(\s|$)", f"import {new_import}\\1", new_content)

        # Update path strings in code
        new_content = new_content.replace(old_rel, new_rel)

        if content != new_content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  Warning: Could not update {file_path}: {e}")
        return False


def find_and_update_references(file_path: Path, old_path: str, new_path: str) -> List[Path]:
    """Find all files that reference the moved file and update them."""
    updated_files = []
    old_rel = old_path.replace("\\", "/")
    new_rel = new_path.replace("\\", "/")
    old_name = Path(old_path).name
    new_name = Path(new_path).name

    search_extensions = [".py", ".md", ".yaml", ".yml", ".txt", ".ps1", ".sh"]

    for ext in search_extensions:
        for ref_file in PROJECT_ROOT.rglob(f"*{ext}"):
            if ref_file == file_path:
                continue
            try:
                content = ref_file.read_text(encoding="utf-8")

                # Check for references
                has_ref = old_rel in content or old_name in content or old_path in content

                if has_ref:
                    new_content = content.replace(old_rel, new_rel)
                    new_content = new_content.replace(old_name, new_name)

                    if content != new_content:
                        ref_file.write_text(new_content, encoding="utf-8")
                        updated_files.append(ref_file)
                        print(f"  Updated: {ref_file.relative_to(PROJECT_ROOT)}")
            except Exception:
                continue

    return updated_files


def move_and_update(
    source: Path, target: Path, updated_imports: List[str], updated_refs: List[str]
) -> Tuple[bool, int]:
    """Move file and update all references."""
    if not source.exists():
        print(f"  Warning: Source not found: {source}")
        return False, 0

    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    # Update imports in the moved file itself
    changed = update_imports_in_file(
        source, str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT))
    )

    # Update references in other files
    refs = find_and_update_references(
        source, str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT))
    )

    # Move the file
    try:
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        source.unlink()
        print(f"  Moved: {source.relative_to(PROJECT_ROOT)} -> {target.relative_to(PROJECT_ROOT)}")
        updated_imports.append(str(source.relative_to(PROJECT_ROOT)))
        for ref in refs:
            updated_refs.append(str(ref.relative_to(PROJECT_ROOT)))
        return True, len(refs)
    except Exception as e:
        print(f"  Error moving {source}: {e}")
        return False, 0


def main():
    print("=" * 70)
    print("REPOSITORY ORGANIZATION - FULL VERSION WITH AUTO-UPDATES")
    print("=" * 70)

    updated_imports = []
    updated_refs = []
    success_count = 0
    fail_count = 0

    # Define file movements
    moves = [
        # maintenance/ (from scripts/utils/)
        ("scripts/utils/check_status.ps1", "scripts/maintenance/check_status.ps1"),
        ("scripts/utils/quick_test.py", "scripts/maintenance/quick_test.py"),
        ("scripts/utils/restore_coverage.py", "scripts/maintenance/restore_coverage.py"),
        # backup/ (from scripts/)
        ("scripts/search_backup.ps1", "scripts/backup/search_backup.ps1"),
        ("scripts/verify_hashes.ps1", "scripts/backup/verify_hashes.ps1"),
        # analyzers/ (from tools/)
        ("tools/check_duplicates.py", "tools/analyzers/check_duplicates.py"),
        ("tools/check_rules.py", "tools/analyzers/check_rules.py"),
        ("tools/check_skills.py", "tools/analyzers/check_skills.py"),
        ("tools/check_skills_duplicates.py", "tools/analyzers/check_skills_duplicates.py"),
        ("tools/check_teacher_duplicates.py", "tools/analyzers/check_teacher_duplicates.py"),
        ("tools/workspace_analyzer.py", "tools/analyzers/workspace_analyzer.py"),
        # debuggers/ (from scripts/diagnostics/)
        ("scripts/diagnostics/health_check.py", "tools/debuggers/health_check.py"),
        ("scripts/diagnostics/complete_diagnostic.py", "tools/debuggers/complete_diagnostic.py"),
        ("scripts/diagnostics/debug_pytest_config.py", "tools/debuggers/debug_pytest_config.py"),
        # automation/ (from scripts/automation/) - FIXED consolidate_adrs.py
        ("scripts/automation/consolidate_adrs.py", "tools/automation/consolidate_adrs.py"),
        ("scripts/automation/consolidate_cases.py", "tools/automation/consolidate_cases.py"),
        ("scripts/automation/start_dev.py", "tools/automation/start_dev.py"),
    ]

    # Create directories first
    print("\n1. Creating new directory structure...")
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
    print("\n2. Moving files and updating references...")
    for source, target in moves:
        src = PROJECT_ROOT / source
        tgt = PROJECT_ROOT / target
        moved, refs_count = move_and_update(src, tgt, updated_imports, updated_refs)
        if moved:
            success_count += 1
            print(f"  Updated {refs_count} references")
        else:
            fail_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Files moved successfully: {success_count}")
    print(f"Files failed: {fail_count}")
    print(f"Import paths updated: {len(set(updated_imports))}")
    print(f"References updated: {len(set(updated_refs))}")

    print("\nNext steps:")
    print("1. Run 'git status' to see all changes")
    print("2. Run 'git diff' to review changes")
    print("3. Run 'git add -u' to stage deleted files")
    print("4. Run 'git add <new_directories>' to stage new files")
    print("5. Run 'git commit -m \"organize: ...\"' to commit")
    print("6. Run 'git push' to push to remote")


if __name__ == "__main__":
    main()
