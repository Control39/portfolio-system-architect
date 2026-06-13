#!/usr/bin/env python3
"""
Generate dynamic badges section for README.md
"""

import json
from pathlib import Path

REPO_ROOT = Path.cwd()
METRICS_FILE = REPO_ROOT / "metrics.json"


def load_metrics():
    """Загрузить метрики"""
    if not METRICS_FILE.exists():
        print("⚠️  metrics.json не найден. Запусти collect_metrics.py сначала.")
        return None

    with open(METRICS_FILE) as f:
        return json.load(f)


def generate_badges_section(metrics):
    """Генерировать секцию с бейджами"""

    return """<!-- REAL METRICS - Updated automatically -->
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
| **K8s Resources** | {k8s} | Production-grade Kubernetes configuration |
| **Dockerfiles** | {dockerfiles} | One per service + utility containers |

---
""".format(
        py_files=metrics["python_files"],
        test_files=metrics["test_files"],
        services=metrics["microservices"],
        loc=f"{metrics['lines_of_code'] / 1000:.1f}k" if metrics["lines_of_code"] > 1000 else metrics["lines_of_code"],
        commits=metrics["git_commits"],
        branches=metrics["git_branches"],
        k8s=metrics["k8s_files"],
        dockerfiles=metrics["dockerfiles"],
    )


def update_readme(badges_section):
    """Обновить README.md"""
    readme_path = REPO_ROOT / "README.md"

    if not readme_path.exists():
        print("❌ README.md не найден!")
        return False

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    # Найти точку для вставки (после первого # Title)
    lines = content.split("\n")
    insert_position = 0

    for i, line in enumerate(lines):
        if line.startswith("# ") and i > 0:
            # Вставить после первого заголовка
            insert_position = i + 1
            break

    # Удалить старую секцию если существует
    new_lines = []
    skip_section = False
    for line in lines:
        if line.startswith("<!-- REAL METRICS"):
            skip_section = True
            continue
        if skip_section and line.startswith("---"):
            skip_section = False
            continue
        if not skip_section:
            new_lines.append(line)

    # Вставить новую секцию
    if insert_position < len(new_lines):
        new_lines.insert(insert_position + 1, badges_section)
    else:
        new_lines.append("\n" + badges_section)

    # Написать обратно
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print("✅ README.md обновлен с реальными бейджами!")
    return True


if __name__ == "__main__":
    metrics = load_metrics()
    if metrics:
        badges = generate_badges_section(metrics)
        update_readme(badges)
        print("\n" + badges)
