"""
Проверка структуры репозитория.
"""

import os
from pathlib import Path

def run(repo_root: str) -> dict:
    required = [
        "apps", "src", "tests", "docs", "deployment", "diagrams",
        "scripts", "tools", ".github", ".env.example", ".gitignore",
        ".dockerignore", ".pre-commit-config.yaml", "README.md",
        "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
        "pyproject.toml", "requirements-dev.txt", "Makefile"
    ]
    missing = []
    for item in required:
        path = Path(repo_root) / item
        if not path.exists():
            missing.append(item)
    return {
        "passed": len(missing) == 0,
        "missing": missing,
        "message": f"Отсутствуют: {missing}" if missing else "Структура соответствует"
    }

if __name__ == "__main__":
    import sys
    result = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(result)