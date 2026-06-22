#!/usr/bin/env python3
"""Generate requirements.txt from Pipfile.lock with exact versions"""
import json
from pathlib import Path

# Read Pipfile.lock
pipfile_lock_path = Path("C:/repo/Pipfile.lock")
with open(pipfile_lock_path, "r", encoding="utf-8") as f:
    pipfile_lock = json.load(f)

# Extract packages with exact versions
packages = pipfile_lock.get("default", {})
dev_packages = pipfile_lock.get("develop", {})

# Generate requirements lines
requirements = []
for package, info in sorted(packages.items()):
    version = info.get("version", "")
    if version.startswith("=="):
        requirements.append(f"{package}{version}")
    elif "git" in info:
        # Handle git dependencies
        git_info = info.get("git", "")
        egg = info.get("egg", package)
        ref = info.get("ref", "main")
        requirements.append(f"-e git+{git_info}@{ref}#egg={egg}")
    else:
        requirements.append(f"{package}=={info.get('version', '*')}")

# Add dev packages
requirements.append("")
requirements.append("# Dev dependencies")
for package, info in sorted(dev_packages.items()):
    version = info.get("version", "")
    if version.startswith("=="):
        requirements.append(f"{package}{version}")
    elif "git" in info:
        git_info = info.get("git", "")
        egg = info.get("egg", package)
        ref = info.get("ref", "main")
        requirements.append(f"-e git+{git_info}@{ref}#egg={egg}")
    else:
        requirements.append(f"{package}=={info.get('version', '*')}")

# Write to requirements.txt - use actual newlines, not escaped
requirements_path = Path("C:/repo/requirements.txt")
with open(requirements_path, "w", encoding="utf-8") as f:
    for req in requirements:
        f.write(req + "\n")

print(f"Generated requirements.txt with {len(requirements)} lines")
print(f"  Default packages: {len(packages)}")
print(f"  Dev packages: {len(dev_packages)}")
print("\nFirst 15 lines of requirements.txt:")
for line in requirements[:15]:
    print(f"  {line}")
