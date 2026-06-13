#!/usr/bin/env python
"""Generate root structure from git-tracked files."""

import subprocess

files = subprocess.check_output(["git", "ls-files"], encoding="utf-8").splitlines()
root_items = sorted(set(f.split("/")[0] for f in files))

with open(".reports/verifications/github-root-structure.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(root_items))

print(f"Generated {len(root_items)} root items")
