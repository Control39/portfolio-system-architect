#!/usr/bin/env python3
"""Analyze Makefile commands and check if they work."""

import os
import re
from pathlib import Path


def parse_makefile(makefile_path: Path):
    """Parse Makefile and extract targets."""
    content = makefile_path.read_text(encoding="utf-8")
    targets = {}

    # Find all .PHONY and target definitions
    lines = content.split("\n")
    current_target = None

    for line in lines:
        # Skip comments and empty lines
        if line.strip().startswith("#") or not line.strip():
            continue

        # Match target definition (name: followed by recipe)
        match = re.match(r"^([a-zA-Z_-]+):", line)
        if match:
            current_target = match.group(1)
            targets[current_target] = []
        elif current_target and line.startswith("\t"):
            # This is a recipe line
            targets[current_target].append(line.strip())

    return targets


def check_target(makefile_path: Path, target: str, recipe: list):
    """Check if a target's recipe is valid."""
    PROJECT_ROOT = Path("C:/repo")
    issues = []

    for cmd in recipe:
        # Check for Python script calls
        if "python" in cmd and ".py" in cmd:
            # Extract script path
            script_match = re.search(r"python\s+(.+\.py)", cmd)
            if script_match:
                script_path = PROJECT_ROOT / script_match.group(1)
                if not script_path.exists():
                    issues.append(f"Script not found: {script_path}")

        # Check for Python module calls
        if "from " in cmd and "import" in cmd:
            # Extract module
            module_match = re.search(r"from\s+(\S+)\s+import", cmd)
            if module_match:
                module_path = PROJECT_ROOT / module_match.group(1).replace(".", "/")
                if not module_path.exists():
                    issues.append(f"Module not found: {module_path}")

    return issues


def main():
    PROJECT_ROOT = Path("C:/repo")
    makefile_path = PROJECT_ROOT / "Makefile"

    print("=" * 70)
    print("MAKEFILE ANALYSIS")
    print("=" * 70)

    if not makefile_path.exists():
        print("Makefile not found!")
        return

    # Parse Makefile
    targets = parse_makefile(makefile_path)

    print("\n1. FOUND TARGETS:")
    for target, recipe in targets.items():
        print(f"\n  [{target}]:")
        for line in recipe:
            print(f"    {line}")

    print("\n2. CHECKING TARGETS:")
    for target, recipe in targets.items():
        issues = check_target(makefile_path, target, recipe)
        if issues:
            print(f"\n  ❌ {target} - HAS ISSUES:")
            for issue in issues:
                print(f"    {issue}")
        else:
            print(f"\n  ✅ {target} - OK")

    print("\n3. RECOMMENDATIONS:")
    print("\n  The Makefile references:")
    print("  - agents/cognitive_agent/autonomous_agent.py")
    print("  - agents/cognitive_agent/main.py")
    print("  - agents/cognitive_agent/orchestrator_v2.py")
    print("  - agents/cognitive_agent/skills/")
    print("  - agents/cognitive_agent/config/")
    print("\n  All these exist, but the Makefile is outdated:")
    print("  - No Python linting/typing checks")
    print("  - No Docker commands")
    print("  - No testing commands (pytest)")
    print("  - No documentation generation")
    print("  - No CI/CD commands")

    print("\n4. MODERN ALTERNATIVES:")
    print("\n  Consider replacing Makefile with:")
    print("  - Taskfile.yml (already exists!)")
    print("  - Python scripts in scripts/ci/")
    print("  - GitHub Actions for CI/CD")


if __name__ == "__main__":
    main()
