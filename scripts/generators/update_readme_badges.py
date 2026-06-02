#!/usr/bin/env python3
"""
Update README.md with dynamic badges from metrics.json
"""

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
METRICS_FILE = REPO_ROOT / "metrics.json"
README_FILE = REPO_ROOT / "README.md"


def load_metrics():
    """Load metrics from JSON file"""
    if not METRICS_FILE.exists():
        print("⚠️  metrics.json not found. Run collect_metrics.py first.")
        return None

    with open(METRICS_FILE) as f:
        return json.load(f)


def generate_badges_section(metrics):
    """Generate badges HTML section"""
    py_files = metrics.get("py_files", 0)
    test_files = metrics.get("test_files", 0)
    services = metrics.get("services", 0)
    loc = metrics.get("loc", 0)
    commits = metrics.get("commits", 0)
    branches = metrics.get("branches", 0)
    k8s = metrics.get("k8s_resources", 0)
    dockerfiles = metrics.get("dockerfiles", 0)

    return f"""<!-- REAL METRICS - Updated automatically -->
## 📊 REAL METRICS (Updated Automatically)

<p align="center">
  <img src="https://img.shields.io/badge/Python%20Files-{py_files}-blue?style=flat-square" alt="Python Files">
  <img src="https://img.shields.io/badge/Test%20Files-{test_files}-green?style=flat-square" alt="Test Files">
  <img src="https://img.shields.io/badge/Microservices-{services}-brightgreen?style=flat-square" alt="Microservices">
  <img src="https://img.shields.io/badge/Lines%20of%20Code-{loc}-orange?style=flat-square" alt="Lines of Code">
  <img src="https://img.shields.io/badge/Git%20Commits-{commits}-purple?style=flat-square" alt="Git Commits">
  <img src="https://img.shields.io/badge/Git%20Branches-{branches}-blue?style=flat-square" alt="Git Branches">
  <img src="https://img.shields.io/badge/K8s%20Resources-{k8s}-informational?style=flat-square" alt="K8s Resources">
  <img src="https://img.shields.io/badge/Dockerfiles-{dockerfiles}-ff69b4?style=flat-square" alt="Dockerfiles">
</p>

### What These Numbers Mean

| Metric | Value | Meaning |
|--------|-------|---------|
| **Python Files** | {py_files} | Complete codebase across all services |
| **Test Files** | {test_files} | Unit, integration, and e2e tests |
| **Microservices** | {services} | Independent deployable services |
| **Lines of Code** | {loc} | Actual implementation (excluding tests & dependencies) |
| **Git Commits** | {commits} | Full development history |
| **Git Branches** | {branches} | Active development branches |
| **K8s Resources** | {k8s} | Kubernetes manifests and configurations |
| **Dockerfiles** | {dockerfiles} | Container definitions |
"""


def update_readme():
    """Update README.md with new badges"""
    metrics = load_metrics()
    if not metrics:
        print("❌ Could not load metrics. Exiting.")
        return False

    badges_section = generate_badges_section(metrics)

    # Read current README
    with open(README_FILE, encoding="utf-8") as f:
        content = f.read()

    # Find and replace the metrics section
    pattern = r"<!-- REAL METRICS - Updated automatically -->.*?(?=\n\n## |\Z)"
    new_content = re.sub(pattern, badges_section, content, flags=re.DOTALL)

    # Check if content changed
    if new_content == content:
        print("✅ README.md already up to date")
        return False

    # Write updated README
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README.md updated with new badges")
    return True


if __name__ == "__main__":
    updated = update_readme()
    exit(0 if updated else 1)
