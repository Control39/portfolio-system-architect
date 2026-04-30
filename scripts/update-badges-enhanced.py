#!/usr/bin/env python3
"""Улучшенный скрипт для автоматического обновления бейджей на основе реальных файлов конфигурации.
Интегрируется в CI/CD для полной автоматизации.
"""

import json
import os
import re
import subprocess
import tomllib
from datetime import datetime
from pathlib import Path


def get_python_version() -> str:
    """Получить версию Python из pyproject.toml или .python-version."""
    try:
        # Пробуем прочитать из pyproject.toml
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                # Проверяем различные места, где может быть указана версия Python
                if "tool" in data and "poetry" in data["tool"]:
                    if "dependencies" in data["tool"]["poetry"]:
                        deps = data["tool"]["poetry"]["dependencies"]
                        if "python" in deps:
                            return deps["python"].replace("^", "").replace("~", "")
    except Exception:
        pass

    # Пробуем прочитать из .python-version
    python_version_path = Path(".python-version")
    if python_version_path.exists():
        return python_version_path.read_text().strip()

    # Пробуем получить из runtime
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Извлекаем только номер версии (например, "Python 3.13.5" -> "3.13.5")
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", version)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Warning: Could not determine Python version: {e}")

    print("Warning: Could not determine Python version, using default 3.13.5")
    return "3.13.5"  # default for development


def get_coverage_percentage() -> float:
    """Получить процент покрытия тестами из coverage report."""
    try:
        # Запускаем pytest с coverage
        result = subprocess.run(
            ["pytest", "--cov=.", "--cov-report=term-missing", "--cov-fail-under=0"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )

        # Ищем процент покрытия в выводе
        for line in result.stdout.split("\n"):
            if "TOTAL" in line and "%" in line:
                # Пример строки: "TOTAL   1234   567   89%"
                parts = line.split()
                for part in parts:
                    if "%" in part:
                        return float(part.replace("%", ""))
    except Exception as e:
        print(f"Error getting coverage: {e}")

    print("Warning: Could not determine test coverage, returning 0")
    return 0.0  # indicates measurement failure


def get_test_status() -> str:
    """Получить статус тестов (passed/failed)."""
    try:
        result = subprocess.run(
            ["pytest", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        return "passed" if result.returncode == 0 else "failed"
    except Exception as e:
        print(f"Error getting test status: {e}")
        return "unknown"


def get_last_commit_date() -> str:
    """Получить дату последнего коммита."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting last commit date: {e}")
        return datetime.now().strftime("%Y-%m-%d")


def get_dependency_count() -> int:
    """Получить количество зависимостей."""
    try:
        # Пробуем прочитать из requirements.txt
        req_path = Path("requirements.txt")
        if req_path.exists():
            with open(req_path, encoding="utf-8") as f:
                lines = f.readlines()
                # Считаем только непустые строки и не комментарии
                count = sum(
                    1 for line in lines if line.strip() and not line.startswith("#")
                )
                return count

        # Пробуем прочитать из pyproject.toml
        pyproject_path = Path("pyproject.toml")
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                if "project" in data and "dependencies" in data["project"]:
                    return len(data["project"]["dependencies"])
    except Exception as e:
        print(f"Error getting dependency count: {e}")

    print("Warning: Could not determine dependency count, returning 0")
    return 0  # indicates unknown count


def update_readme_badges():
    """Обновить бейджи в README.md на основе текущих метрик."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found")
        return

    content = readme_path.read_text(encoding="utf-8")

    # Получаем текущие метрики
    python_version = get_python_version()
    coverage = get_coverage_percentage()
    test_status = get_test_status()
    last_commit = get_last_commit_date()
    dependency_count = get_dependency_count()

    print("Current metrics:")
    print(f"  Python: {python_version}")
    print(f"  Coverage: {coverage}%")
    print(f"  Test status: {test_status}")
    print(f"  Last commit: {last_commit}")
    print(f"  Dependencies: {dependency_count}")

    # Обновляем Python version badge
    python_badge = f'<img src="https://img.shields.io/badge/Python-{python_version}-blue?style=flat-square&logo=python" alt="Python {python_version}">'
    content = re.sub(
        r'<img src="https://img.shields.io/badge/Python-[^>]+>',
        python_badge,
        content,
    )

    # Обновляем Coverage badge (статический)
    coverage_badge = f'<img src="https://img.shields.io/badge/Coverage-{coverage:.1f}%25-{"brightgreen" if coverage >= 80 else "yellow"}?style=flat-square" alt="Code Coverage">'
    content = re.sub(
        r'<img src="https://img.shields.io/badge/Coverage-[^>]+>',
        coverage_badge,
        content,
    )

    # Обновляем Test status badge
    test_color = "green" if test_status == "passed" else "red"
    test_badge = f'<img src="https://img.shields.io/badge/Tests-{test_status}-{test_color}?style=flat-square&logo=pytest" alt="Test Status">'

    if '<img src="https://img.shields.io/badge/Tests-' not in content:
        # Вставляем после coverage badge
        coverage_pattern = r'(<img src="https://img.shields.io/badge/Coverage-[^>]+>)'
        content = re.sub(coverage_pattern, f"\\1\n  {test_badge}", content)
    else:
        content = re.sub(
            r'<img src="https://img.shields.io/badge/Tests-[^>]+>',
            test_badge,
            content,
        )

    # Добавляем/обновляем бейдж зависимостей
    deps_badge = f'<img src="https://img.shields.io/badge/Dependencies-{dependency_count}-blue?style=flat-square&logo=pypi" alt="Dependencies">'

    if '<img src="https://img.shields.io/badge/Dependencies-' not in content:
        # Вставляем после Python badge
        python_pattern = r'(<img src="https://img.shields.io/badge/Python-[^>]+>)'
        content = re.sub(python_pattern, f"\\1\n  {deps_badge}", content)
    else:
        content = re.sub(
            r'<img src="https://img.shields.io/badge/Dependencies-[^>]+>',
            deps_badge,
            content,
        )

    # Записываем обновленный README
    readme_path.write_text(content, encoding="utf-8")
    print("README badges updated successfully")

    # Сохраняем метрики для CI
    metrics = {
        "python_version": python_version,
        "coverage": coverage,
        "test_status": test_status,
        "last_commit": last_commit,
        "dependency_count": dependency_count,
        "updated_at": datetime.now().isoformat(),
    }

    metrics_path = Path("badges/metrics.json")
    metrics_path.parent.mkdir(exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Metrics saved to {metrics_path}")


def main():
    """Основная функция."""
    print("Updating README badges based on current configuration files...")
    update_readme_badges()

    # Также обновляем badges/coverage.md для GitHub Pages
    coverage = get_coverage_percentage()
    badges_dir = Path("badges")
    badges_dir.mkdir(exist_ok=True)

    coverage_md = badges_dir / "coverage.md"
    coverage_md.write_text(
        f"![Test Coverage](https://img.shields.io/badge/coverage-{coverage:.1f}%25-{'brightgreen' if coverage >= 80 else 'yellow'})\n\n"
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        encoding="utf-8",
    )
    print(f"Coverage badge updated in {coverage_md}")


if __name__ == "__main__":
    main()
