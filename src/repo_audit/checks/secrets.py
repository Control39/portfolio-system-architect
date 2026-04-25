"""
Проверка секретов в репозитории.
"""

import subprocess

def run(repo_root: str) -> dict:
    # Попробуем detect-secrets
    try:
        r = subprocess.run(
            ["detect-secrets", "scan"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        if "Found" in r.stdout:
            return {
                "passed": False,
                "message": "Обнаружены возможные секреты",
                "output": r.stdout[:500]
            }
        else:
            return {
                "passed": True,
                "message": "Секреты не обнаружены"
            }
    except FileNotFoundError:
        # detect-secrets не установлен
        return {
            "passed": True,
            "message": "detect-secrets не установлен, пропуск"
        }
    except Exception as e:
        return {
            "passed": False,
            "message": f"Ошибка при проверке секретов: {e}"
        }

if __name__ == "__main__":
    import sys
    result = run(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(result)
