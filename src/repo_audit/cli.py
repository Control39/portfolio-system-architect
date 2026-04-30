#!/usr/bin/env python3
"""
CLI инструмент для автоматической проверки репозитория по чек-листу.
"""

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_checklist(checklist_path: str) -> Dict[str, Any]:
    """Загрузить YAML чек-листа."""
    with open(checklist_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_check(script_path: str, repo_root: str) -> Dict[str, Any]:
    """Запустить скрипт проверки и вернуть результат."""
    try:
        spec = importlib.util.spec_from_file_location("check_module", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            return module.run(repo_root)
        else:
            return {"passed": False, "error": "Функция run не найдена"}
    except Exception as e:
        return {"passed": False, "error": str(e)}


def execute_shell(cmd: List[str], cwd: str) -> Dict[str, Any]:
    """Выполнить shell команду и вернуть результат."""
    try:
        # shell=False для безопасности, чтобы избежать инъекций команд
        result = subprocess.run(
            cmd, shell=False, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return {
            "passed": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Таймаут выполнения"}
    except Exception as e:
        return {"passed": False, "error": str(e)}


def check_structure(repo_root: str) -> Dict[str, Any]:
    """Проверка структуры репозитория."""
    required = [
        "apps",
        "src",
        "tests",
        "docs",
        "deployment",
        "diagrams",
        "scripts",
        "tools",
        ".github",
        ".env.example",
        ".gitignore",
        ".dockerignore",
        ".pre-commit-config.yaml",
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "pyproject.toml",
        "requirements-dev.txt",
        "Makefile",
    ]
    missing = []
    for item in required:
        path = Path(repo_root) / item
        if not path.exists():
            missing.append(item)
    return {
        "passed": len(missing) == 0,
        "missing": missing,
        "message": f"Отсутствуют: {missing}" if missing else "Структура соответствует",
    }


def check_git(repo_root: str) -> Dict[str, Any]:
    """Проверка git ветвления."""
    # Простая проверка наличия ветки develop
    result = execute_shell(["git", "branch", "--list", "develop"], repo_root)
    develop_exists = "develop" in result.get("stdout", "")
    return {
        "passed": develop_exists,
        "message": "Ветка develop существует"
        if develop_exists
        else "Ветка develop отсутствует",
    }


def check_linting(repo_root: str) -> Dict[str, Any]:
    """Проверка линтинга."""
    results = []
    # ruff
    r = execute_shell(["ruff", "check", "."], repo_root)
    results.append(("ruff", r["passed"]))
    # black
    b = execute_shell(["black", "--check", "."], repo_root)
    results.append(("black", b["passed"]))
    # isort
    i = execute_shell(["isort", "--check-only", "."], repo_root)
    results.append(("isort", i["passed"]))
    passed = all(p for _, p in results)
    return {
        "passed": passed,
        "details": results,
        "message": "Линтинг пройден" if passed else "Ошибки линтинга",
    }


def check_secrets(repo_root: str) -> Dict[str, Any]:
    """Проверка секретов."""
    # Если detect-secrets установлен
    r = execute_shell(["detect-secrets", "scan"], repo_root)
    # Если есть найденные секреты
    if "Found" in r.get("stdout", ""):
        return {"passed": False, "message": "Обнаружены возможные секреты"}
    return {"passed": True, "message": "Секреты не обнаружены"}


def check_ci(repo_root: str) -> Dict[str, Any]:
    """Проверка CI."""
    ci_path = Path(repo_root) / ".github" / "workflows" / "ci.yml"
    if ci_path.exists():
        return {"passed": True, "message": "CI workflow существует"}
    else:
        return {"passed": False, "message": "CI workflow отсутствует"}


def run_audit(checklist_path: str, repo_root: str, level: str = None) -> Dict[str, Any]:
    """Запустить аудит по чек-листу."""
    checklist = load_checklist(checklist_path)
    results = []
    total_checks = 0
    passed_checks = 0

    for lvl in checklist["levels"]:
        if level and lvl["id"] != level:
            continue
        for check in lvl["checks"]:
            total_checks += 1
            check_id = check["id"]
            check_name = check["name"]
            automated = check.get("automated", False)
            if automated:
                script = check.get("script")
                if script:
                    # запуск скрипта
                    script_path = Path(repo_root) / "repo_audit" / script
                    if script_path.exists():
                        result = run_check(str(script_path), repo_root)
                    else:
                        result = {"passed": False, "error": "Скрипт не найден"}
                else:
                    # встроенные проверки
                    if check_id == "repo_structure":
                        result = check_structure(repo_root)
                    elif check_id == "git_branching":
                        result = check_git(repo_root)
                    elif check_id == "linting_formatting":
                        result = check_linting(repo_root)
                    elif check_id == "secrets_check":
                        result = check_secrets(repo_root)
                    elif check_id == "basic_ci":
                        result = check_ci(repo_root)
                    else:
                        result = {"passed": False, "error": "Проверка не реализована"}
            else:
                result = {"passed": None, "message": "Ручная проверка"}
            passed = result.get("passed", False)
            if passed:
                passed_checks += 1
            results.append(
                {
                    "level": lvl["id"],
                    "check": check_id,
                    "name": check_name,
                    "passed": passed,
                    "details": result,
                }
            )

    return {
        "summary": {
            "total": total_checks,
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "score": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
        },
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Аудит репозитория по чек-листу")
    parser.add_argument(
        "--checklist", default="repo_audit/checklist.yaml", help="Путь к чек-листу"
    )
    parser.add_argument("--repo", default=".", help="Корень репозитория")
    parser.add_argument("--level", help="Уровень (level1, level2, level3)")
    parser.add_argument(
        "--output", choices=["text", "json"], default="text", help="Формат вывода"
    )
    args = parser.parse_args()

    results = run_audit(args.checklist, args.repo, args.level)

    if args.output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("АУДИТ РЕПОЗИТОРИЯ")
        print("=" * 60)
        for r in results["results"]:
            status = (
                "✅ ПРОЙДЕН"
                if r["passed"]
                else "❌ НЕ ПРОЙДЕН"
                if r["passed"] is False
                else "⚠️  РУЧНАЯ"
            )
            print(f"{r['level']}.{r['check']}: {r['name']} - {status}")
            if "details" in r and r["details"].get("message"):
                print(f"   {r['details']['message']}")
        print("=" * 60)
        s = results["summary"]
        print(f"ИТОГО: {s['passed']}/{s['total']} пройдено ({s['score']:.1f}%)")
        if s["score"] >= 80:
            print("🎉 Репозиторий соответствует высокому уровню зрелости!")
        elif s["score"] >= 50:
            print("📈 Есть потенциал для улучшения.")
        else:
            print("🚨 Требуется серьёзная доработка.")


if __name__ == "__main__":
    main()
