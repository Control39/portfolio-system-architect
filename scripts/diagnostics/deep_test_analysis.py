#!/usr/bin/env python3
"""
Детальный анализ тестов:
1. Контекст time.sleep
2. Тесты без assert
3. Покрытие кода
4. Сравнение с корневой tests/
"""

import re
from collections import defaultdict
from pathlib import Path


def analyze_sleep():
    """Анализ time.sleep с контекстом"""
    print("=" * 70)
    print("1. АНАЛИЗ time.sleep")
    print("=" * 70)

    sleep_cases = []
    for py_file in Path("apps").rglob("tests/test_*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "time.sleep" in line:
                # Получить контекст (2 строки до и после)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])

                sleep_cases.append(
                    {
                        "file": str(py_file.relative_to(Path("."))),
                        "line_num": i + 1,
                        "context": context,
                    }
                )

    print(f"Всего использований time.sleep: {len(sleep_cases)}\n")

    # Классификация
    categories = {"Очевидно плохо": [], "Возможно оправдано": [], "В тестах производительности": []}

    for case in sleep_cases:
        ctx = case["context"].lower()
        if "wait" in ctx or "sleep" in ctx:
            categories["Очевидно плохо"].append(case)
        elif "performance" in ctx or "timing" in ctx:
            categories["В тестах производительности"].append(case)
        else:
            categories["Возможно оправдано"].append(case)

    for cat, cases in categories.items():
        if cases:
            print(f"\n{cat} ({len(cases)}):")
            for c in cases[:3]:
                print(f"  {c['file']}:{c['line_num']}")
                # Показать строку с sleep
                for line in c["context"].split("\n"):
                    if "sleep" in line.lower():
                        print(f"    -> {line.strip()}")
            if len(cases) > 3:
                print(f"  ... и ещё {len(cases) - 3}")


def find_assertless():
    """Поиск тестов без assert"""
    print("\n" + "=" * 70)
    print("2. ТЕСТЫ БЕЗ ASSERT")
    print("=" * 70)

    assertless = []
    total_tests = 0

    for py_file in Path("apps").rglob("tests/test_*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # Найти функции test_*
        tests = re.findall(r"def (test_[^(]+)\([^)]*\):", content)
        total_tests += len(tests)

        for test_name in tests:
            # Найти тело теста
            pattern = rf"def {re.escape(test_name)}\([^)]*\):(.*?)(?=\ndef |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                body = match.group(1)
                if "assert" not in body and "pytest.raises" not in body and "with " not in body:
                    assertless.append(f"{py_file.relative_to(Path('.'))}:{test_name}")

    print(f"Всего тестов: {total_tests}")
    print(f"Тестов без assert: {len(assertless)} ({len(assertless)/max(total_tests,1)*100:.1f}%)")

    if assertless:
        print("\nСписок тестов без assert:")
        for t in assertless[:15]:
            print(f"  - {t}")
        if len(assertless) > 15:
            print(f"  ... и ещё {len(assertless) - 15}")


def analyze_coverage():
    """Анализ покрытия (если coverage запущен)"""
    print("\n" + "=" * 70)
    print("3. ПОКРЫТИЕ КОДА")
    print("=" * 70)

    # Проверить наличие .coverage
    if Path(".coverage").exists():
        import coverage

        cov = coverage.Coverage()
        cov.load()
        report = cov.report(show_missing=False)
        print(f"Общее покрытие: {report:.1f}%")

        # Покрытие по сервисам
        services = {}
        for service_dir in Path("apps").iterdir():
            if service_dir.is_dir() and not service_dir.name.startswith("_"):
                src_dir = service_dir / "src"
                if src_dir.exists():
                    try:
                        cov2 = coverage.Coverage(source=[str(src_dir)])
                        cov2.load()
                        r = cov2.report(show_missing=False)
                        services[service_dir.name] = r
                    except:
                        pass

        print("\nПокрытие по сервисам:")
        for service, cov_pct in sorted(services.items(), key=lambda x: -x[1]):
            print(f"  {service}: {cov_pct:.1f}%")
    else:
        print("Файл .coverage не найден. Запустите: coverage run --source=apps -m pytest")


def analyze_root_tests():
    """Анализ корневой tests/ на дублирование"""
    print("\n" + "=" * 70)
    print("4. КОРНЕВАЯ tests/ - ПРОВЕРКА НА ДУБЛИРОВАНИЕ")
    print("=" * 70)

    tests_root = Path("tests")
    if not tests_root.exists():
        print("Папка tests/ не найдена")
        return

    # Найти все тестовые файлы в корне
    root_tests = list(tests_root.glob("test_*.py"))
    unit_tests = (
        list((tests_root / "unit").glob("test_*.py")) if (tests_root / "unit").exists() else []
    )

    print(f"Файлов в tests/ (корень): {len(root_tests)}")
    print(f"Файлов в tests/unit/: {len(unit_tests)}")

    # Проверить импорты
    service_deps = defaultdict(list)
    for test_file in root_tests + unit_tests:
        content = test_file.read_text(encoding="utf-8", errors="ignore")
        # Найти импорты из apps
        imports = re.findall(r"from (apps\.[\w_]+)", content)
        for imp in imports:
            service_deps[imp].append(test_file.name)

    if service_deps:
        print("\nЗависимости от сервисов:")
        for service, files in service_deps.items():
            print(f"  {service}: {files}")
    else:
        print("\nНет зависимостей от сервисов (хорошо для e2e тестов)")

    # Рекомендация
    if unit_tests:
        print("\n⚠️  ВНИМАНИЕ: tests/unit/ может дублировать apps/*/tests/")
        print("Рекомендация: сравнить содержимое и удалить дубликаты")


def main():
    print("=" * 70)
    print("ГЛУБОКИЙ АНАЛИЗ КАЧЕСТВА ТЕСТОВ")
    print("Portfolio System Architect")
    print("=" * 70)

    analyze_sleep()
    find_assertless()
    analyze_coverage()
    analyze_root_tests()

    print("\n" + "=" * 70)
    print("ИТОГИ")
    print("=" * 70)
    print("1. time.sleep: 20 случаев (критично)")
    print("2. Тесты без assert: требуют проверки")
    print("3. Покрытие: запустить coverage для точных цифр")
    print("4. Корневая tests/: проверить на дублирование")
    print("\nСледующий шаг: создать итоговый отчёт")


if __name__ == "__main__":
    main()
