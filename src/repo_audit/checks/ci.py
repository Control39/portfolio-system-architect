"""Проверка наличия CI workflow.
"""

from pathlib import Path


def run(repo_root: str) -> dict:
    ci_path = Path(repo_root) / ".github" / "workflows" / "ci.yml"
    if ci_path.exists():
        return {
            "passed": True,
            "message": "CI workflow существует",
        }
    # проверим другие возможные имена
    alt = list(Path(repo_root).glob(".github/workflows/*.yml")) + \
              list(Path(repo_root).glob(".github/workflows/*.yaml"))
    if alt:
        return {
            "passed": True,
            "message": f"Найдены workflow: {[p.name for p in alt]}",
        }
    return {
        "passed": False,
        "message": "CI workflow отсутствует",
    }

if __name__ == "__main__":
    import sys
    result = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(result)

