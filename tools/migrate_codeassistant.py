#!/usr/bin/env python3
"""Скрипт переноса .codeassistant в .agents и архив"""

import shutil
from pathlib import Path

BASE = Path.cwd()
CODEASSISTANT = BASE / ".codeassistant"
AGENTS = BASE / ".agents"
ARCHIVE = BASE / ".archive" / "codeassistant_backup"


def copy_merge(src: Path, dst: Path):
    """Копирует или сливает директории"""
    if not src.exists():
        print(f"⚠️  {src} не существует")
        return
    if not dst.exists():
        dst.mkdir(parents=True)

    for item in src.iterdir():
        dest = dst / item.name
        if item.is_dir():
            print(f"📁 {'Merge' if dest.exists() else 'Copy'}: {item.name}")
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            print(f"📄 Copy: {item.name}")
            shutil.copy2(item, dest)


def main():
    print("🚀 Начало переноса .codeassistant -> .agents")

    # 1. Скиллы
    print("\n--- Скиллы ---")
    copy_merge(CODEASSISTANT / "skills", AGENTS / "skills")

    # 2. Планы
    print("\n--- Планы ---")
    copy_merge(CODEASSISTANT / "plans", AGENTS / "plans")

    # 3. Teacher
    print("\n--- Teacher ---")
    copy_merge(CODEASSISTANT / "teacher", AGENTS / "teacher")

    # 4. Tools (если нужны)
    print("\n--- Tools ---")
    copy_merge(CODEASSISTANT / "tools", AGENTS / "tools")

    # 5. Rules
    print("\n--- Rules ---")
    copy_merge(CODEASSISTANT / "rules", AGENTS / "rules")

    # 6. Конфиги (mcp.json, ai-models.yaml) - только если актуальны
    # Пропускаем, так как у нас уже есть обновленные версии

    # 7. Архивация .codeassistant
    print("\n--- Архивация .codeassistant ---")
    if ARCHIVE.exists():
        print(f"⚠️  Архив уже существует: {ARCHIVE}")
        choice = input("Удалить старый архив и создать новый? (y/n): ")
        if choice.lower() == "y":
            shutil.rmtree(ARCHIVE)
        else:
            print("❌ Отмена архивации")
            return

    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    print(f"📦 Перемещение {CODEASSISTANT} -> {ARCHIVE}")
    shutil.move(str(CODEASSISTANT), str(ARCHIVE))
    print("✅ Архивация завершена")

    print("\n🎉 Перенос завершен!")
    print(f"📂 Архив: {ARCHIVE}")
    print(f"📂 Активные скиллы: {AGENTS / 'skills'}")


if __name__ == "__main__":
    main()
