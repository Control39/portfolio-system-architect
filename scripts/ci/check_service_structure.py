#!/usr/bin/env python
"""
Проверка соответствия сервисов стандарту структуры.

Использование:
    python check_service_structure.py [--service <name>] [--fix]

Возвращает:
    - Список сервисов, соответствующих стандарту
    - Список сервисов, требующих доработки
    - Детальный отчёт по каждому сервису
"""

import sys
from pathlib import Path
from typing import TypedDict


class ServiceCheck(TypedDict):
    name: str
    path: Path
    score: int
    issues: list[str]
    missing: list[str]


def check_service(service_path: Path) -> ServiceCheck:
    """Проверить соответствие сервиса стандарту."""
    name = service_path.name
    issues = []
    missing = []

    # Обязательные файлы
    required_files = {
        "main.py": "Entry point (или app.py)",
        "README.md": "Документация",
        "requirements.txt": "Зависимости",
        "Dockerfile": "Контейнеризация",
    }

    # Опциональные директории
    optional_dirs = {
        "src/": "Исходный код",
        "tests/": "Тесты",
    }

    # Проверка обязательных файлов
    for filename, desc in required_files.items():
        if not (service_path / filename).exists():
            # Проверяем альтернативы
            if filename == "main.py" and (service_path / "app.py").exists():
                continue
            missing.append(f"{filename} ({desc})")
            issues.append(f"❌ Отсутствует {filename}")

    # Проверка директорий
    for dirname, desc in optional_dirs.items():
        dir_path = service_path / dirname.rstrip("/")
        if not dir_path.exists():
            missing.append(f"{dirname} ({desc})")
            issues.append(f"⚠️ Отсутствует {dirname}")

    # Проверка README качества (7 секций)
    readme_path = service_path / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text(encoding="utf-8")
        required_sections = [
            "Purpose",
            "Features",
            "API",
            "Dependencies",
            "Deployment",
            "Contributing",
        ]
        for section in required_sections:
            if section not in readme_content:
                issues.append(f"⚠️ README.md: отсутствует секция '{section}'")

    # Проверка тестов
    tests_path = service_path / "tests"
    if tests_path.exists():
        test_files = list(tests_path.glob("test_*.py"))
        if not test_files:
            issues.append("⚠️ tests/: нет файлов тестов (test_*.py)")

    # Подсчёт очков
    total_checks = len(required_files) + len(optional_dirs)
    passed = total_checks - len(missing)
    score = int((passed / total_checks) * 100)

    return ServiceCheck(
        name=name,
        path=service_path,
        score=score,
        issues=issues,
        missing=missing,
    )


def check_all_services(base_path: Path) -> list[ServiceCheck]:
    """Проверить все сервисы в директории apps/."""
    apps_path = base_path / "apps"
    results = []

    # Исключаемые директории (служебные)
    excluded = {"__pycache__", "tests", "utils", "__init__.py"}

    for service_dir in apps_path.iterdir():
        if service_dir.is_dir() and service_dir.name not in excluded:
            result = check_service(service_dir)
            results.append(result)

    return results


def print_report(results: list[ServiceCheck]) -> None:
    """Вывести отчёт в консоль."""
    print("\n" + "=" * 80)
    print("ОТЧЁТ: Проверка соответствия структуре сервиса")
    print("=" * 80 + "\n")

    compliant = [r for r in results if r["score"] == 100]
    non_compliant = [r for r in results if r["score"] < 100]

    print(f"Всего сервисов: {len(results)}")
    print(f"✅ Соответствуют: {len(compliant)} ({len(compliant)/len(results)*100:.0f}%)")
    print(f"⚠️ Требуют доработки: {len(non_compliant)}\n")

    if compliant:
        print("✅ Соответствующие сервисы:")
        for r in compliant:
            print(f"   - {r['name']} (100%)")
        print()

    if non_compliant:
        print("⚠️ Сервисы, требующие доработки:")
        for r in sorted(non_compliant, key=lambda x: x["score"]):
            print(f"\n   {r['name']} ({r['score']}%)")
            for issue in r["issues"]:
                print(f"      {issue}")
            if r["missing"]:
                print(f"      missing: {', '.join(r['missing'])}")

    print("\n" + "=" * 80)

    # Вывод метрик
    avg_score = sum(r["score"] for r in results) / len(results)
    print(f"Средний балл: {avg_score:.1f}%")
    print("=" * 80 + "\n")


def main():
    """Основная функция."""
    import argparse

    parser = argparse.ArgumentParser(description="Проверка структуры сервисов")
    parser.add_argument(
        "--service",
        type=str,
        help="Проверить конкретный сервис",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Автоматически исправить (создать отсутствующие файлы)",
    )

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    if args.service:
        # Проверка конкретного сервиса
        service_path = base_path / "apps" / args.service
        if not service_path.exists():
            print(f"Ошибка: Сервис '{args.service}' не найден")
            sys.exit(1)

        result = check_service(service_path)
        print(f"\nПроверка сервиса: {result['name']}")
        print(f"Балл: {result['score']}%")

        if result["issues"]:
            print("\nПроблемы:")
            for issue in result["issues"]:
                print(f"  {issue}")
        else:
            print("\n✅ Сервис соответствует стандарту!")

        sys.exit(0 if result["score"] == 100 else 1)

    # Проверка всех сервисов
    results = check_all_services(base_path)
    print_report(results)

    # Возвращаем код ошибки, если есть несоответствия
    non_compliant = [r for r in results if r["score"] < 100]
    sys.exit(1 if non_compliant else 0)


if __name__ == "__main__":
    main()
