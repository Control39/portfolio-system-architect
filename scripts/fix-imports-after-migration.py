#!/usr/bin/env python3
"""
Скрипт для обновления импортов после миграции директорий:
- .agents/ → apps/cognitive-agent/
- .codeassistant/ → codeassistant/

ВАЖНО: Сначала нужно выполнить git mv для директорий!

Запуск: python scripts/fix-imports-after-migration.py
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

    # Проверка миграции директорий
    old_agents = project_root / ".agents"
    new_cognitive_agent = project_root / "apps" / "cognitive-agent"
    old_codeassistant = project_root / ".codeassistant"
    new_codeassistant = project_root / "codeassistant"

    print("🔍 Проверка миграции директорий...")

    if old_agents.exists() and not new_cognitive_agent.exists():
        print("⚠️  .agents/ существует, apps/cognitive-agent/ не существует")
        print("💡 Сначала выполните: git mv .agents apps/cognitive-agent")
        return

    if old_codeassistant.exists() and not new_codeassistant.exists():
        print("⚠️  .codeassistant/ существует, codeassistant/ не существует")
        print("💡 Сначала выполните: git mv .codeassistant codeassistant")
        return

    # Если директории уже перемещены, обновляем только импорты в коде
    if not old_agents.exists() and not old_codeassistant.exists():
        print("✅ Директории уже перемещены, обновляем импорты в коде...")

        # Списки замен только для кода (не документации)
        replacements = [
            # .agents/ → apps/cognitive-agent/
            (".agents/config/", "apps/cognitive-agent/config/"),
            (".agents/skills/", "apps/cognitive-agent/skills/"),
            (".agents/workflows/", "apps/cognitive-agent/workflows/"),
            (".agents/data/", "apps/cognitive-agent/data/"),
            (".agents/reports/", "apps/cognitive-agent/reports/"),
            (".agents/scans/", "apps/cognitive-agent/scans/"),
            (".agents/plans/", "apps/cognitive-agent/plans/"),
            (".agents/changelogs/", "apps/cognitive-agent/changelogs/"),
            (".agents/metrics/", "apps/cognitive-agent/metrics/"),
            # .codeassistant/ → codeassistant/
            (".codeassistant/", "codeassistant/"),
        ]

        # Расширения файлов для обработки
        code_extensions = [".py", ".ts", ".js", ".yaml", ".yml", ".json", ".md"]

        changed_files = []

        for root, dirs, files in os.walk(project_root):
            # Пропускаем исключённые директории
            exclude_dirs = [
                ".git",
                ".venv",
                "__pycache__",
                ".pytest_cache",
                "node_modules",
                ".ruff_cache",
                ".mypy_cache",
            ]
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not any(file.endswith(ext) for ext in code_extensions):
                    continue

                # Пропускаем бинарные файлы
                if any(file.endswith(ext) for ext in [".pyc", ".pyo", ".so", ".dll", ".exe"]):
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
        print(f"📊 ИТОГИ:")
        print(f"   Исправлено файлов: {len(changed_files)}")

        if changed_files:
            print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
            print("1. Проверить изменения: git diff")
            print("2. Запустить линтеры: ruff check .")
            print("3. Закоммитить: git add . && git commit -m 'fix: обновить импорты после миграции'")
        else:
            print("\n✅ Все импорты актуальны!")


if __name__ == "__main__":
    main()
