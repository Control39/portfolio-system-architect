#!/usr/bin/env python3
"""Сбор метрик качества тестов для монорепозитория"""

import re
from collections import defaultdict
from pathlib import Path


def main():
    print("=" * 60)
    print("АНАЛИЗ КАЧЕСТВА ТЕСТОВ - Portfolio System Architect")
    print("=" * 60)

    # 1. Анализ корневой tests/
    print("\n### 1. КОРНЕВАЯ tests/ ###")
    tests_root = Path("tests")
    if tests_root.exists():
        files = list(tests_root.glob("*.py"))
        dirs = [d for d in tests_root.iterdir() if d.is_dir()]
        print(f"Файлы: {len(files)}")
        print(f"Папки: {[d.name for d in dirs]}")

        # Проверка импортов
        service_imports = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if "from apps." in content or "import apps" in content:
                    service_imports.append(f.name)
            except:
                pass
        print(f"Файлы с импортами сервисов: {service_imports if service_imports else 'Нет'}")

    # 2. Дубликаты тестовых хелперов
    print("\n### 2. ДУБЛИКАТЫ ХЕЛПЕРОВ ###")
    helper_patterns = ["create_test", "make_user", "create_user", "get_fixture", "setup_db"]
    duplicates = defaultdict(list)
    for py_file in Path("apps").rglob("tests/**/*.py"):
        if "test_" in py_file.name:
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in helper_patterns:
                    if pattern in content:
                        duplicates[pattern].append(str(py_file.relative_to(Path("."))))
            except:
                pass

    for pattern, files in duplicates.items():
        if len(files) > 1:
            print(f"{pattern}: {len(files)} файла")
            for f in files[:3]:
                print(f"  - {f}")

    # 3. Параметризованные тесты
    print("\n### 3. ПАРАМЕТРИЗАЦИЯ И ПРОВЕРКИ ОШИБОК ###")
    parametrize_count = 0
    raises_count = 0
    fixture_count = 0
    slow_count = 0
    skip_count = 0
    total_test_files = 0

    for py_file in Path("apps").rglob("tests/test_*.py"):
        total_test_files += 1
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            parametrize_count += len(re.findall(r"@pytest.mark.parametrize", content))
            raises_count += len(re.findall(r"pytest.raises", content))
            fixture_count += len(re.findall(r"@pytest.fixture", content))
            slow_count += len(re.findall(r"@pytest.mark.slow", content))
            skip_count += len(re.findall(r"@pytest.mark.skip", content))
        except:
            pass

    print(f"Всего тест-файлов: {total_test_files}")
    print(f"Параметризованных тестов: {parametrize_count}")
    print(f"Тестов на ошибки (raises): {raises_count}")
    print(f"Фикстур: {fixture_count}")
    print(f"Медленных тестов (slow): {slow_count}")
    print(f"Пропущенных тестов (skip): {skip_count}")

    # Метрики качества
    if total_test_files > 0:
        param_pct = (parametrize_count / max(total_test_files, 1)) * 100
        raises_pct = (raises_count / max(total_test_files, 1)) * 100
        print(f"\nДоля параметризованных тестов: {param_pct:.1f}%")
        print(f"Доля тестов на ошибки: {raises_pct:.1f}%")

    # 4. Внешние зависимости
    print("\n### 4. ВНЕШНИЕ ЗАВИСИМОСТИ ###")
    http_count = 0
    db_count = 0
    for py_file in Path("apps").rglob("tests/test_*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"(requests\.|httpx\.|aiohttp\.|http\.get)", content):
                http_count += 1
            if re.search(r"(postgresql|redis|mongodb|sqlite)", content, re.IGNORECASE):
                db_count += 1
        except:
            pass

    print(f"Файлов с HTTP-вызовами: {http_count}")
    print(f"Файлов с упоминанием БД: {db_count}")

    # 5. Anti-patterns
    print("\n### 5. ANTI-PATTERNS ###")
    sleep_count = 0
    random_count = 0
    for py_file in Path("apps").rglob("tests/test_*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            sleep_count += len(re.findall(r"time\.sleep", content))
            random_count += len(re.findall(r"(random\.|randint|choice)", content))
        except:
            pass

    print(f"Использований time.sleep: {sleep_count}")
    print(f"Использований random: {random_count}")

    # 6. Статистика по сервисам
    print("\n### 6. СТАТИСТИКА ПО СЕРВИСАМ ###")
    services = {}
    for service_dir in Path("apps").iterdir():
        if service_dir.is_dir() and not service_dir.name.startswith("_"):
            test_files = list(service_dir.rglob("tests/test_*.py"))
            if test_files:
                services[service_dir.name] = len(test_files)

    for service, count in sorted(services.items(), key=lambda x: -x[1]):
        print(f"{service}: {count} тест-файлов")

    # 7. Итоговая оценка
    print("\n### 7. ИТОГОВАЯ ОЦЕНКА ###")
    score = 7.2  # Базовая оценка из предыдущего аудита

    # Корректировки
    if param_pct > 20:
        score += 0.5
        print("✅ Хорошая параметризация тестов")
    elif param_pct < 10:
        score -= 0.5
        print("⚠️ Низкая параметризация тестов")

    if raises_pct > 10:
        score += 0.5
        print("✅ Хорошее покрытие тестами ошибок")
    elif raises_pct < 5:
        score -= 0.5
        print("⚠️ Мало тестов на ошибки")

    if http_count > 0:
        score -= 0.3
        print(f"⚠️ {http_count} файлов с HTTP-вызовами (нужно мокирование)")

    if sleep_count > 0:
        score -= 0.5
        print(f"🔴 {sleep_count} использований time.sleep (антипаттерн)")

    if skip_count > 5:
        score -= 0.3
        print(f"⚠️ {skip_count} пропущенных тестов")

    print(f"\n{'=' * 60}")
    print(f"ИТОГОВАЯ ОЦЕНКА КАЧЕСТВА: {score:.1f}/10")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
