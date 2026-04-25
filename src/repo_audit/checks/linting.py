"""Проверка линтинга и форматирования.
"""

import subprocess


def run(repo_root: str) -> dict:
    results = []
    # ruff
    r = subprocess.run(
        ["ruff", "check", "."],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    results.append(("ruff", r.returncode == 0, r.stdout[:200] if r.stdout else ""))
    # black
    b = subprocess.run(
        ["black", "--check", "."],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    results.append(("black", b.returncode == 0, b.stdout[:200] if b.stdout else ""))
    # isort
    i = subprocess.run(
        ["isort", "--check-only", "."],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    results.append(("isort", i.returncode == 0, i.stdout[:200] if i.stdout else ""))

    passed = all(p for _, p, _ in results)
    return {
        "passed": passed,
        "details": [{"tool": t, "passed": p, "output": o} for t, p, o in results],
        "message": "Линтинг пройден" if passed else "Ошибки линтинга",
    }

if __name__ == "__main__":
    import sys
    result = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(result)
