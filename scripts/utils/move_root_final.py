#!/usr/bin/env python3
"""
Move root files to appropriate locations based on analysis.
Follows Python best practices and project conventions.
"""

import shutil
from pathlib import Path


PROJECT_ROOT = Path("C:/repo")

# Define all movements
moves = {
    # scripts/utils/ - utility scripts
    "scripts/utils": [
        "conftest.py",
        "pytest_debug.py",
        "trace_pytest_paths.py",
        "notify_github.py",
        "update_dependencies.py",
        "update_pipfile.py",
        "count_lines.py",
        "generate_requirements.py",
    ],
    # scripts/ci/ - CI/CD checks
    "scripts/ci": [
        "check_bandit_files.py",
        "check_bandit_full.py",
        "check_bandit_high.py",
        "check_pytest_ini.py",
        "check_pytest_paths.py",
        "check_pytest_paths2.py",
        "check_scripts_bandit.py",
        "check_src_bandit.py",
        "check_tools_bandit.py",
        "check_vulns.py",
        "check_syntax.py",
        "check_toml.py",
    ],
    # scripts/maintenance/ - maintenance scripts
    "scripts/maintenance": [
        "fix_all_empty_if.py",
        "fix_all_empty_if_v2.py",
        "fix_all_nosec.py",
        "fix_bandit_exclude.py",
        "fix_bandit_high.py",
        "fix_mcp_syntax.py",
        "fix_nosec.py",
        "fix_nosec_final.py",
        "fix_precommit.py",
        "fix_remaining_bandit.py",
        "fix_vscode_subprocess.py",
        "fix_vscode_subprocess2.py",
    ],
    # scripts/automation/ - automation scripts
    "scripts/automation": [
        "find_empty_if.py",
        "find_indent_errors.py",
    ],
    # tests/ - test files
    "tests": [
        "test_agent_methods.py",
        "test_conftest_import.py",
        "test_conftest_paths.py",
        "test_exact_syspath.py",
        "test_exact_syspath2.py",
        "test_final_import.py",
        "test_final_import2.py",
        "test_import_cm.py",
        "test_import_debug.py",
        "test_import_direct.py",
        "test_import_order.py",
        "test_paths.py",
        "test_paths_direct.py",
        "test_path_order.py",
        "test_syspath_simulation.py",
    ],
    # scripts/dev/ - development/debug tools
    "scripts/dev": [
        "debug_taskfile.py",
    ],
}

# Files to delete
delete_files = [
    "bandit-report-full.json",
    "bandit-report.json",
    "coverage.json",
    "vulnerabilities.json",
    "trivy-secret.yaml",
    "phase2_integration_test_results.json",
]


def move_file(source: str, target_dir: str) -> bool:
    """Move a file and return success status."""
    source_path = PROJECT_ROOT / source
    target_path = PROJECT_ROOT / target_dir / Path(source).name

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
    print("MOVE ROOT FILES - FINAL ORGANIZATION")
    print("=" * 70)

    success = 0
    fail = 0

    # 1. Create directories
    print("\n1. Creating target directories...")
    dirs = list(moves.keys())
    for d in dirs:
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d}")

    # 2. Move all files
    print("\n2. Moving files...")
    for target_dir, files in moves.items():
        for source in files:
            if move_file(source, target_dir):
                success += 1
            else:
                fail += 1

    # 3. Delete temp files
    print("\n3. Deleting temporary files...")
    for temp in delete_files:
        if delete_file(temp):
            success += 1
        else:
            fail += 1

    # 4. Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: Success={success}, Fail={fail}")
    print("=" * 70)

    print("\n✅ Files moved to appropriate locations:")
    for target in moves.keys():
        count = len(moves[target])
        print(f"  {target}/: {count} files")

    print("\n✅ Temp files deleted:")
    print(f"  {len(delete_files)} files")

    print("\n📁 Files remaining in root (standard config/docs):")
    standard = [
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
        "Pipfile.lock",
        "Makefile",
        "Justfile",
        "Taskfile.yml",
        "tox.ini",
        "pytest.ini",
        "pyrightconfig.json",
        "renovate.json",
        "sonar-project.properties",
        "docker-compose.yml",
        "docker-compose.jaeger.yml",
        ".pre-commit-config.yaml",
        ".editorconfig",
    ]
    for f in standard:
        if (PROJECT_ROOT / f).exists():
            print(f"  ✓ {f}")

    print("\n📝 Next steps:")
    print("1. Review changes with 'git status'")
    print("2. Commit moved files: 'git add -u && git add <moved dirs>'")
    print("3. Commit: 'git commit -m \"clean: organize root directory\"'")
    print("4. Push: 'git push origin main'")


if __name__ == "__main__":
    main()
