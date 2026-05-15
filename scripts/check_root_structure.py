#!/usr/bin/env python
"""Check if github-root-structure.txt is up to date."""

import subprocess


# Get current root items from git
files = subprocess.check_output(["git", "ls-files"], encoding="utf-8").splitlines()
current_roots = sorted(set(f.split("/")[0] for f in files))

# Read stored root items
with open(".reports/verifications/github-root-structure.txt", encoding="utf-8") as f:
    stored_roots = sorted(f.read().splitlines())

# Compare
if current_roots == stored_roots:
    print("✅ File is UP TO DATE!")
    print(f"   {len(current_roots)} root items match.")
else:
    print("❌ File is OUT OF DATE!")
    added = set(current_roots) - set(stored_roots)
    removed = set(stored_roots) - set(current_roots)
    if added:
        print(f"   Added: {sorted(added)}")
    if removed:
        print(f"   Removed: {sorted(removed)}")
    # Update file
    with open(".reports/verifications/github-root-structure.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(current_roots))
    print("   -> File updated.")
