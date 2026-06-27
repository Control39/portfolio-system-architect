#!/usr/bin/env python3
"""Скрипт копирования файлов из бэкапа .codeassistant."""

import os
import shutil
from pathlib import Path

backup_path = Path(r"C:\1cognitive-systems-architecture.codeassistant")
target_path = Path(r"C:\repo\.codeassistant")
conflicts_file = target_path / "CONFLICTS_SKIPPED.txt"

conflicts = []
copied_count = 0

# Создаем целевую директорию если нет
target_path.mkdir(exist_ok=True)

for root, dirs, files in os.walk(backup_path):
    for file in files:
        src_file = Path(root) / file
        rel_path = src_file.relative_to(backup_path)
        dst_file = target_path / rel_path

        if dst_file.exists():
            conflicts.append(str(rel_path))
            print(f"⏭️  Пропущено (существует): {rel_path}")
        else:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied_count += 1
            print(f"✅ Скопировано: {rel_path}")

# Сохраняем список конфликтов
with open(conflicts_file, "w", encoding="utf-8") as f:
    f.write("# Конфликты при восстановлении из backup\n\n")
    f.write("Дата: 26 мая 2026\n")
    f.write(f"Скопировано файлов: {copied_count}\n")
    f.write(f"Пропущено (уже существовали): {len(conflicts)}\n\n")
    f.write("## Список пропущенных файлов:\n\n")
    for conflict in conflicts:
        f.write(f"- {conflict}\n")

print(f"\n{'=' * 50}")
print("ИТОГ:")
print(f"✅ Скопировано: {copied_count} файлов")
print(f"⏭️  Пропущено (конфликты): {len(conflicts)} файлов")
print(f"📄 Список конфликтов: {conflicts_file}")

if conflicts:
    print("\n⚠️  Внимание! Следующие файлы были пропущены, так как уже существуют:")
    for c in conflicts:
        print(f"   - {c}")
