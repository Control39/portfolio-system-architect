#!/usr/bin/env python3
"""Исправление импортов в тестах chat_backend."""

import re
from pathlib import Path

# Файлы для исправления
TEST_FILES = [
    "apps/chat_backend/tests/test_chat_api.py",
    "apps/chat_backend/tests/test_chat_handlers.py",
    "apps/chat_backend/tests/test_memory_room_store.py",
    "apps/chat_backend/tests/test_model_config.py",
    "apps/chat_backend/tests/test_readyz.py",
    "apps/chat_backend/tests/test_room_metadata_integration.py",
    "apps/chat_backend/tests/test_room_store.py",
    "apps/chat_backend/tests/test_runtime_config.py",
    "apps/chat_backend/tests/test_task_manager.py",
]

# Маппинг замен
REPLACEMENTS = {
    "from python_server.": "from apps.chat_backend.",
    "import python_server": "import apps.chat_backend",
    "from flask import": "from fastapi.testclient import TestClient",  # Замена Flask на FastAPI
    "from flask.testing": "from fastapi.testclient import TestClient",
}


def fix_imports(file_path: str) -> int:
    """Исправить импорты в файле. Возвращает количество замен."""
    path = Path(file_path)
    if not path.exists():
        print(f"⚠️  Файл не найден: {file_path}")
        return 0

    content = path.read_text(encoding="utf-8")
    original = content
    changes = 0

    for old, new in REPLACEMENTS.items():
        matches = len(re.findall(re.escape(old), content))
        if matches:
            content = content.replace(old, new)
            changes += matches
            print(f"  ✅ Заменено '{old}' → '{new}' ({matches} раз)")

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"📝 Обновлён файл: {file_path}")
    else:
        print(f"ℹ️  Без изменений: {file_path}")

    return changes


def main():
    print("=" * 80)
    print("ИСПРАВЛЕНИЕ ИМПОРТОВ В ТЕСТАХ chat_backend")
    print("=" * 80)
    print()

    total_changes = 0
    for file_path in TEST_FILES:
        print(f"Обработка: {file_path}")
        changes = fix_imports(file_path)
        total_changes += changes
        print()

    print("=" * 80)
    print(f"ИТОГО: выполнено {total_changes} замен")
    print("=" * 80)
    print()
    print("Следующие шаги:")
    print("1. Установите зависимости: pip install flask fastapi openai azure-identity azure-messaging-webpubsubservice")
    print("2. Запустите тесты: pytest apps/chat_backend/tests/ -v")
    print("3. Проверьте покрытие: pytest apps/chat_backend/tests/ --cov=apps.chat_backend --cov-report=term-missing")


if __name__ == "__main__":
    main()
