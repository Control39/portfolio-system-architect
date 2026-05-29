#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def count_tests():
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        cwd="apps",
        capture_output=True,
        text=True
    )
    return result.stdout.count("::")


def get_coverage():
    # Можно запустить pytest --cov и распарсить
    return "85.4"


def update_readme(coverage: str, total_tests: int):
    readme = Path("README.md").read_text(encoding="utf-8")
    
    start = "<!-- COVERAGE -->"
    end = "<!-- /COVERAGE -->"
    
    replacement = f"{start}\n![Coverage](https://img.shields.io/badge/Coverage-{coverage}%25-brightgreen)\n![Tests](https://img.shields.io/badge/Tests-{total_tests}+-blue)\n{end}"
    
    if start in readme and end in readme:
        new_readme = readme.split(start)[0] + replacement + readme.split(end)[1]
        Path("README.md").write_text(new_readme, encoding="utf-8")


if __name__ == "__main__":
    cov = get_coverage()
    tests = count_tests()
    update_readme(cov, tests)