#!/usr/bin/env python3
"""
Скрипт для исправления старых импортов после миграции:
- apps/cognitive-agent/ → apps/cognitive-agent/
- codeassistant/ → codeassistant/ (уже правильный путь)

Запуск: python scripts/fix-old-imports.py
"""

import os
from pathlib import Path


def replace_in_file(filepath: Path, replacements: list[tuple[str, str]]) -> bool:
    """Заменяет строки в файле и возвращает True, если были изменения."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        for old, new in replacements:
            content = content.replace(old, new)

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"❌ Ошибка при обработке {filepath}: {e}")
        return False


def main():
    project_root = Path(__file__).parent.parent

    # Списки замен
    replacements = [
        # apps/cognitive-agent/ → apps/cognitive-agent/
        ("apps/cognitive-agent/config/", "apps/cognitive-agent/config/"),
        ("apps/cognitive-agent/skills/", "apps/cognitive-agent/skills/"),
        ("apps/cognitive-agent/workflows/", "apps/cognitive-agent/workflows/"),
        ("apps/cognitive-agent/data/", "apps/cognitive-agent/data/"),
        ("apps/cognitive-agent/reports/", "apps/cognitive-agent/reports/"),
        ("apps/cognitive-agent/scans/", "apps/cognitive-agent/scans/"),
        ("apps/cognitive-agent/plans/", "apps/cognitive-agent/plans/"),
        ("apps/cognitive-agent/changelogs/", "apps/cognitive-agent/changelogs/"),
        ("apps/cognitive-agent/metrics/", "apps/cognitive-agent/metrics/"),
        ("apps/cognitive-agent/", "apps/cognitive-agent/"),
        # codeassistant/ → codeassistant/ (убираем точку)
        ("codeassistant/", "codeassistant/"),
    ]

    # Файлы/директории, которые нужно исключить
    exclude_patterns = [
        ".git/",
        ".venv/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "node_modules/",
        "*.md",  # Документацию не трогаем пока
    ]

    changed_files = []

    print("🔍 Поиск файлов с устаревшими импортами...")

    for root, dirs, files in os.walk(project_root):
        # Пропускаем исключённые директории
        dirs[:] = [d for d in dirs if not any(pat.strip("/") in d for pat in exclude_patterns)]

        for file in files:
            # Пропускаем бинарные и исключённые файлы
            if any(file.endswith(ext) for ext in [".pyc", ".pyo", ".so", ".dll", ".exe"]):
                continue
            if any(pat in file for pat in exclude_patterns):
                continue

            filepath = Path(root) / file

            # Проверяем, есть ли в файле старые импорты
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if not any(old in content for old, _ in replacements):
                        continue
            except:
                continue

            # Исправляем импорты
            if replace_in_file(filepath, replacements):
                changed_files.append(filepath)
                print(f"✅ Исправлен: {filepath.relative_to(project_root)}")

    print("\n" + "=" * 60)
    print("📊 ИТОГИ:")
    print(f"   Исправлено файлов: {len(changed_files)}")

    if changed_files:
        print("\n📝 Список изменённых файлов:")
        for f in changed_files:
            print(f"   - {f.relative_to(project_root)}")

        print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Проверить изменения: git diff")
        print("2. Запустить линтеры: make lint")
        print("3. Запустить тесты: make test")
        print("4. Закоммитить: git add . && git commit -m 'fix: исправить устаревшие импорты после миграции'")
    else:
        print("\n✅ Все импорты актуальны!")


if __name__ == "__main__":
    main()
