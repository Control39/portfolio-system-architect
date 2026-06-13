#!/usr/bin/env python3
"""
Add git installation to Dockerfiles that use python:slim images.
"""

import re
from pathlib import Path


def add_git_to_dockerfile(filepath):
    """Add git installation after WORKDIR /app."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Check if git is already installed
    if "apt-get.*git" in content or "RUN apt-get" not in content:
        return False

    # Pattern to match WORKDIR /app followed by comments or COPY
    pattern = r"(WORKDIR /app\s*\n)(\s*#.*\n)?(\s*COPY\s+requirements\.txt)"
    replacement = r"\1\n# Install git for pip dependencies from git repos\nRUN apt-get update && apt-get install -y --no-install-recommends \\\n    git \\\n    && rm -rf /var/lib/apt/lists/*\n\n\3"

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ {filepath}")
        return True
    else:
        print(f"⚠️  No match: {filepath}")
        return False


if __name__ == "__main__":
    apps_dir = Path("apps")
    count = 0

    for dockerfile in apps_dir.rglob("Dockerfile"):
        if add_git_to_dockerfile(dockerfile):
            count += 1

    print(f"\n✅ Updated {count} Dockerfiles")
