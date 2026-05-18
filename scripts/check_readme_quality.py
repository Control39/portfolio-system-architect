#!/usr/bin/env python3
"""Проверка качества README микросервисов"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Критерии проверки
CRITERIA = {
    "title": r"^#\s+.+",  # Заголовок # Название
    "purpose": r"(##\s*Назначение|##\s*Purpose|###\s*Что делает|##\s*Overview|##\s*Описание|###\s*Цель)",
    "features": r"(##\s*Ключевые возможности|##\s*Features|##\s*Основные возможности|Ключевые возможности|##\s*Функции|\[\s*x\s*\])",
    "api": r"(\@\@app\.|/api/|endpoints|ENDPOINTS|API\s*Reference|`\//|##\s*API|###\s*Endpoints)",
    "dependencies": r"(requirements|Dependencies|dependencies|pip install|###\s*Установка|##\s*Установка|###\s*Зависимости|##\s*Зависимости)",
    "deployment": r"(docker|Docker|compose|Deploy|deploy|port\s*[:=]|localhost:\d+|run\s*`|##\s*Запуск|###\s*Запуск)",
    "contributing": r"(contributing|Contributing|как внести|how to|CONTRIBUTING|Вклад|##\s*Вклад|###\s*Вклад)",
}


def check_readme(service_name: str, readme_path: Path) -> Dict[str, bool]:
    """Проверить README на наличие критериев"""
    if not readme_path.exists():
        return {k: False for k in CRITERIA}

    content = readme_path.read_text(encoding="utf-8")
    results = {}

    for criterion, pattern in CRITERIA.items():
        results[criterion] = bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))

    return results


def analyze_services(apps_dir: Path) -> List[Dict]:
    """Проверить все сервисы в apps/"""
    results = []

    for service_dir in sorted(apps_dir.iterdir()):
        if not service_dir.is_dir():
            continue
        if service_dir.name.startswith("_") or service_dir.name == "tests":
            continue

        readme_path = service_dir / "README.md"
        checks = check_readme(service_dir.name, readme_path)
        score = sum(checks.values())
        max_score = len(CRITERIA)

        results.append({
            "name": service_dir.name,
            "has_readme": readme_path.exists(),
            "score": score,
            "max_score": max_score,
            "checks": checks,
            "path": readme_path,
        })

    return results


def print_report(results: List[Dict]) -> None:
    """Вывести отчет в консоль"""
    print("=" * 80)
    print("ПРОВЕРКА КАЧЕСТВА README МИКРОСЕРВИСОВ")
    print("=" * 80)
    print()

    # Заголовки
    header = f"{'Сервис':<25} {'Оценка':<10} {'Назначение':<12} {'API':<6} {'Deps':<6} {'Deploy':<8} {'Contrib':<8}"
    print(header)
    print("-" * len(header))

    for r in results:
        if not r["has_readme"]:
            print(f"{r['name']:<25} {'НЕТ README':<10}")
            continue

        checks = r["checks"]
        print(
            f"{r['name']:<25} "
            f"{r['score']}/{r['max_score']:<9} "
            f"{'✓' if checks['purpose'] else '✗':<12} "
            f"{'✓' if checks['api'] else '✗':<6} "
            f"{'✓' if checks['dependencies'] else '✗':<6} "
            f"{'✓' if checks['deployment'] else '✗':<8} "
            f"{'✓' if checks['contributing'] else '✗':<8}"
        )

    print()

    # Итоги
    total = len(results)
    with_readme = sum(1 for r in results if r["has_readme"])
    perfect = sum(1 for r in results if r["score"] == r["max_score"])
    needs_work = sum(1 for r in results if r["has_readme"] and r["score"] < r["max_score"])

    print("ИТОГИ:")
    print(f"  Всего сервисов: {total}")
    print(f"  С README: {with_readme}/{total} ({100*with_readme//total}%)")
    print(f"  Идеальные (6/6): {perfect}")
    print(f"  Требуют улучшения: {needs_work}")
    print()

    # Сервисы с проблемами
    problems = [r for r in results if r["has_readme"] and r["score"] < 4]
    if problems:
        print("⚠️  Сервисы с низким качеством README (< 4 баллов):")
        for r in problems:
            print(f"  - {r['name']}: {r['score']}/{r['max_score']}")
            missing = [k for k, v in r["checks"].items() if not v]
            print(f"    Пропущено: {', '.join(missing)}")
        print()


def main():
    """Основная функция"""
    apps_dir = Path(__file__).parent / "apps"

    if not apps_dir.exists():
        print(f"Ошибка: папка {apps_dir} не найдена")
        return

    results = analyze_services(apps_dir)
    print_report(results)


if __name__ == "__main__":
    main()
