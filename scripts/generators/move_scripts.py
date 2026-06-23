#!/usr/bin/env python3
"""
Скрипт для перемещения скриптов в папки по категориям и создания .scripts/
"""

import os
import shutil


def main():
    print("=== START SCRIPT MOVING ===")

    # Create directories
    scripts_dirs = [
        "scripts/ai",
        "scripts/automation",
        "scripts/ci",
        "scripts/deployment",
        "scripts/dev",
        "scripts/diagnostics",
        "scripts/generators",
        "scripts/git",
        "scripts/linux",
        "scripts/management",
        "scripts/migration",
        "scripts/python",
        "scripts/security",
        "scripts/utils",
        "scripts/utils_legacy",
        "scripts/windows",
        ".scripts/personal",
        "scripts/build/test"
    ]

    for dir_path in scripts_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created/exists: {dir_path}")

    # Move root files
    files_to_move = [
        ("check_integrations.py", "scripts/diagnostics/check_integrations.py"),
        ("test_fallback_fix.py", "scripts/build/test/test_fallback_fix.py"),
    ]

    for source, dest in files_to_move:
        if os.path.exists(source):
            shutil.move(source, dest)
            print(f"Moved: {source} -> {dest}")

    # List of personal scripts to move to .scripts/personal
    personal_scripts = [
        "agent_self_analyze.py",
        "agent_self_analyze_quick.py",
        "agent_self_analyze.sh",
        "agent_self_analyze_quick.sh",
        "agent_menu.sh",
        "agent_status_check.py",
        "check_gigachat_token.py",
        "check_ports.py",
        "check_service_structure.py",
        "collect_metrics.py",
        "complete_strategic_analyzer.py",
        "cognitive_agent_chat.py",
        "ddd_analyzer.py",
        "ddd_show_dependencies.py",
        "ddd_show_issues.py",
        "generate_badges.py",
        "organize_repo_files.py",
        "run_cognitive_agent.py",
        "run_project_scanner.py",
        "simple_check.py",
        "simple_doc_audit_test.py",
        "strategic_analyzer_full.py",
        "test_ai_connection.py",
        "test_gigachat_connection.py",
        "update_agent_config.py",
        "update_readme_badges.py",
    ]

    # Move personal scripts
    for script in personal_scripts:
        source = f"scripts/{script}"
        dest = f".scripts/personal/{script}"

        if os.path.exists(source):
            shutil.move(source, dest)
            print(f"Moved to .scripts/personal: {script}")

    # Move additional scripts to appropriate folders
    # Check if files are in root and move them to .scripts/personal
    root_scripts = [
        "add_git_to_dockerfiles.py",
        "analyze_dependencies.py",
        "architecture_alignment.py",
        "check_environment.py",
        "cognitive_agent_chat.py",
        "copy_core.py",
        "copy_markdown_files.py",
        "documentation_audit_demo.py",
        "enhanced_agent_demo.py",
        "prevent_blind_add.py",
        "strategic_value_analyzer_web.py",
        "test_code_analyzer_only.py",
    ]

    for script in root_scripts:
        source = script
        dest = f".scripts/personal/{script}"

        if os.path.exists(source):
            shutil.move(source, dest)
            print(f"Moved to .scripts/personal: {script}")

    print("=== SCRIPT MOVING COMPLETED ===")

if __name__ == "__main__":
    main()
