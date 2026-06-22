#!/usr/bin/env python3
"""Update Pipfile to include all packages from current requirements.txt"""
import re
from pathlib import Path

# Read requirements.txt
requirements_path = Path("C:/repo/requirements.txt")
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements_content = f.read()

# Parse requirements.txt - extract package names and versions
packages = []
dev_packages = []
for line in requirements_content.strip().split("\n"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue

    # Skip -e git+ lines for now
    if line.startswith("-e "):
        continue

    # Extract package name and version
    match = re.match(r"([a-zA-Z0-9_-]+)==([0-9.]+)", line)
    if match:
        package_name = match.group(1)
        version = match.group(2)

        # Check if this is a dev package
        dev_keywords = ['pytest', 'black', 'ruff', 'mypy', 'bandit', 'coverage', 'detect-secrets']
        if any(kw in package_name.lower() for kw in dev_keywords):
            dev_packages.append((package_name, version))
        else:
            packages.append((package_name, version))

print(f"Parsed {len(packages)} regular packages and {len(dev_packages)} dev packages")

# Read current Pipfile
pipfile_path = Path("C:/repo/Pipfile")
with open(pipfile_path, "r", encoding="utf-8") as f:
    pipfile_content = f.read()

# Find section positions
packages_section_start = pipfile_content.find("[packages]")
dev_section_start = pipfile_content.find("[dev-packages]")
requires_start = pipfile_content.find("[requires]")

if packages_section_start == -1 or dev_section_start == -1 or requires_start == -1:
    print("ERROR: Could not find section markers in Pipfile")
    exit(1)

# Create new packages section
new_packages_section = "[packages]\n"
for package_name, version in packages:
    new_packages_section += f'{package_name} = "=={version}"\n'

# Create new dev packages section
new_dev_section = "[dev-packages]\n"
for package_name, version in dev_packages:
    new_dev_section += f'{package_name} = "=={version}"\n'

# Reconstruct Pipfile
new_pipfile_content = (
    pipfile_content[:packages_section_start] +
    new_packages_section +
    "\n" +
    new_dev_section +
    "\n" +
    pipfile_content[requires_start:]
)

# Write updated Pipfile
with open(pipfile_path, "w", encoding="utf-8") as f:
    f.write(new_pipfile_content)

print(f"Updated Pipfile with {len(packages)} packages and {len(dev_packages)} dev packages")
print(f"New Pipfile size: {len(new_pipfile_content)} bytes")
