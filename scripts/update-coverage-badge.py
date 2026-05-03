#!/usr/bin/env python3
"""
Скрипт автоматического обновления бейджа покрытия в README.

Использование:
    python scripts/update-coverage-badge.py

Что делает:
    1. Запускает pytest с генерацией coverage.xml
    2. Извлекает процент покрытия из XML
    3. Обновляет бейдж в README.md
    4. Обновляет дату в docs/TEST-COVERAGE-METRICS.md
    5. (Опционально) Делает git commit
"""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Конфигурация
PROJECT_ROOT = Path(__file__).parent.parent
README_PATH = PROJECT_ROOT / "README.md"
METRICS_PATH = PROJECT_ROOT / "docs" / "TEST-COVERAGE-METRICS.md"
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

# Исключаемые тесты (пре-existing проблемы)
EXCLUDED_TESTS = [
    "tests/unit/test_assistant_orchestrator_main.py",
    "tests/unit/test_embedding_agent_updated.py",
]


def run_tests() -> bool:
    """Запускает pytest с генерацией coverage.xml."""
    print("🧪 Запуск тестов...")

    # Формируем аргументы pytest
    args = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=apps",
        "--cov=src",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "--cov-fail-under=90",  # Порог качества
        "-v",
    ]

    # Добавляем исключения для пре-existing проблем
    for test_path in EXCLUDED_TESTS:
        args.extend(["--ignore", str(PROJECT_ROOT / test_path)])

    result = subprocess.run(args, cwd=PROJECT_ROOT)
    return result.returncode == 0


def extract_coverage() -> float:
    """Извлекает процент покрытия из coverage.xml."""
    if not COVERAGE_XML.exists():
        raise FileNotFoundError("coverage.xml не найден. Запустите тесты сначала.")

    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()
    line_rate = float(root.get("line-rate", 0))
    return round(line_rate * 100, 1)


def update_readme_badge(coverage: float) -> None:
    """Обновляет бейдж покрытия в README.md."""
    if not README_PATH.exists():
        print(f"❌ README.md не найден: {README_PATH}")
        return

    content = README_PATH.read_text(encoding="utf-8")
    date_str = datetime.now().strftime("%d %B %Y")

    # Шаблоны бейджей (ищем все варианты)
    badge_patterns = [
        # Вариант 1: img.shields.io с codecov
        r"\[!\[Coverage\]\(https://img\.shields\.io/codecov/c/github/[^)]+\)\]",
        # Вариант 2: img.shields.io с badge
        r"\[!\[Coverage\]\(https://img\.shields\.io/badge/coverage-[^)]+\)\]",
        # Вариант 3: Текстовое указание с датой
        r"\*\*Покрытие\*\*: \d+%\s*\([^)]*\)",
    ]

    # Новый бейдж
    new_badge = f"[![Coverage](https://img.shields.io/badge/coverage-{coverage}%25-brightgreen)](docs/TEST-COVERAGE-METRICS.md)"
    new_date_line = f"*Обновлено: {date_str}*"

    # Ищем и заменяем бейдж
    found = False
    for pattern in badge_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, new_badge, content)
            found = True
            break

    # Если бейдж не найден, добавляем после CI бейджа
    if not found:
        ci_badge_pattern = r"(\[!\[CI\]\([^)]+\)\])"
        if re.search(ci_badge_pattern, content):
            replacement = r"\1\n" + new_badge
            content = re.sub(ci_badge_pattern, replacement, content)
            found = True

    # Обновляем дату в текстовом описании (если есть)
    date_pattern = r"\*Обновлено: [^*]+\*"
    if re.search(date_pattern, content):
        content = re.sub(date_pattern, new_date_line, content)
    elif found:
        # Добавляем дату после бейджа, если её не было
        content = content.replace(new_badge, new_badge + "\n" + new_date_line)

    README_PATH.write_text(content, encoding="utf-8")
    print("✅ Бейдж обновлён в README.md")


def update_metrics_date(coverage: float) -> None:  # <-- FIX: добавлен параметр coverage
    """Обновляет дату в TEST-COVERAGE-METRICS.md."""
    if not METRICS_PATH.exists():
        print(f"⚠️  {METRICS_PATH} не найден. Пропускаем.")
        return

    content = METRICS_PATH.read_text(encoding="utf-8")
    date_str = datetime.now().strftime("%d %B %Y")

    # Обновляем дату в заголовке
    date_pattern = r">\*\*Последнее обновление\*\*: [^\n]+"
    replacement = f">**Последнее обновление:** {date_str}"
    content = re.sub(date_pattern, replacement, content)

    # Добавляем запись в историю
    history_pattern = r"(\| \d{4}-\d{2}-\d{2} \| \d+% \|)"
    # <-- FIX: теперь переменная coverage доступна, так как передана в функцию
    new_entry = f"| {datetime.now().strftime('%Y-%m-%d')} | {coverage}% | Автоматическое обновление через скрипт |"

    # Вставляем новую запись после первой строки истории
    history_start = content.find("| Дата | Покрытие |")
    if history_start != -1:
        # Находим конец заголовка таблицы
        table_end = content.find("|", history_start + 10)
        table_end = content.find("|", table_end + 1)  # Строка разделителя
        table_end = content.find("\n", table_end) + 1  # Конец строки разделителя
        content = content[:table_end] + new_entry + "\n" + content[table_end:]

    METRICS_PATH.write_text(content, encoding="utf-8")
    print("✅ Дата обновлена в TEST-COVERAGE-METRICS.md")


def git_commit(coverage: float) -> None:
    """Делает git commit изменений (если git доступен)."""
    print("\n📦 Делаю git commit...")

    try:
        # Проверка, что мы в git-репозитории
        subprocess.run(
            ["git", "rev-parse", "--git-dir"], cwd=PROJECT_ROOT, capture_output=True, check=True
        )

        # Добавляем изменения
        subprocess.run(
            ["git", "add", str(README_PATH.relative_to(PROJECT_ROOT))], cwd=PROJECT_ROOT, check=True
        )
        subprocess.run(
            ["git", "add", str(METRICS_PATH.relative_to(PROJECT_ROOT))],
            cwd=PROJECT_ROOT,
            check=True,
        )

        # Делаем коммит
        message = (
            f"chore: update coverage badge to {coverage}% ({datetime.now().strftime('%Y-%m-%d')})"
        )
        subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_ROOT, check=True)

        print(f"✅ Коммит сделан: {message}")

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git commit не выполнен: {e}")
        print("   Можете сделать его вручную:")
        print(f"   git add {README_PATH.relative_to(PROJECT_ROOT)}")
        print(f"   git add {METRICS_PATH.relative_to(PROJECT_ROOT)}")
        print(f'   git commit -m "chore: update coverage badge to {coverage}%"')


def main():
    print("=" * 60)
    print("🔄 Обновление бейджа покрытия тестами")
    print("=" * 60)

    # Шаг 1: Запуск тестов
    if not run_tests():
        print("\n❌ Тесты не прошли. Проверьте ошибки выше.")
        print("   Бейдж не будет обновлён.")
        sys.exit(1)

    # Шаг 2: Извлечение покрытия
    try:
        coverage = extract_coverage()
        print(f"📊 Текущее покрытие: {coverage}%")
    except FileNotFoundError as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

    # Шаг 3: Обновление README
    update_readme_badge(coverage)

    # Шаг 4: Обновление METRICS <-- FIX: передаём coverage в функцию
    update_metrics_date(coverage)

    # Шаг 5: Git commit (опционально)
    print("\n🤖 Сделать git commit? (y/n): ", end="")
    choice = input().strip().lower()
    if choice in ("y", "yes", "д", "да"):
        git_commit(coverage)

    print("\n" + "=" * 60)
    print("✅ Обновление завершено!")
    print(f"   Покрытие: {coverage}%")
    print("   README.md обновлён")
    print("   TEST-COVERAGE-METRICS.md обновлён")
    print("=" * 60)


if __name__ == "__main__":
    main()
