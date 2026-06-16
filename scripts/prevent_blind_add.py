#!/usr/bin/env python3
"""
Pre-commit hook: Защита от слепого git add -A / git add .
Проверяет staged-файлы на наличие запрещённых паттернов, секретов и больших файлов.
"""

import os
import re
import subprocess
import sys

# ==============================================================================
# НАСТРОЙКИ ПРАВИЛ
# ==============================================================================
# 1. Запрещённые паттерны (регулярные выражения)
FORBIDDEN_PATTERNS = [
    r"^\.env(\..*)?$",  # .env, .env.local, .env.example
    r"__pycache__/",  # Кэш Python
    r"\.pyc$",  # Скомпилированные файлы Python
    r"\.pytest_cache/",  # Кэш pytest
    r"\.mypy_cache/",  # Кэш mypy
    r"^repo-env/",  # Песочница (защита от случайного коммита)
    r"^\.venv/",  # Виртуальное окружение
    r"\.pem$",  # Приватные ключи
    r"\.key$",  # Ключи шифрования
    r"\.db$",  # Локальные базы данных (SQLite)
]

# 2. Максимальный размер файла в байтах (по умолчанию 5 МБ)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


# ==============================================================================
def get_staged_files():
    """Получает список файлов, добавленных в индекс (staged)"""
    try:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Убираем пустые строки
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Git: не удалось получить список staged-файлов.\n{e.stderr}")
        sys.exit(1)


def check_files(files):
    """Проверяет файлы на соответствие правилам"""
    errors = []
    for file in files:
        # Проверка 1: Запрещённые паттерны
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, file, re.IGNORECASE):
                errors.append(f"🚫 Запрещённый файл/путь: '{file}' (совпадение с правилом: {pattern})")
                break  # Переходим к следующему файлу

        # Проверка 2: Размер файла (если файл физически существует в working tree)
        if os.path.exists(file):
            try:
                size = os.path.getsize(file)
                if size > MAX_FILE_SIZE_BYTES:
                    size_mb = size / (1024 * 1024)
                    errors.append(f"🚫 Файл слишком большой: '{file}' ({size_mb:.2f} МБ > 5 МБ)")
            except OSError:
                pass  # Игнорируем ошибки доступа к файлу

    return errors


def main():
    files = get_staged_files()
    if not files:
        sys.exit(0)  # Нечего проверять

    errors = check_files(files)
    if errors:
        print("\n" + "=" * 70)
        print(" 🛑 PRE-COMMIT ХУК ОТКЛОНИЛ ИЗМЕНЕНИЯ (prevent_blind_add)")
        print("=" * 70)
        print("Обнаружены проблемы в staged-файлах:\n")
        for err in errors:
            print(f"  • {err}")
        print("\n💡 Как исправить:")
        print("  1. Убедись, что эти файлы действительно должны быть в репозитории.")
        print("  2. Если это артефакт сборки или секрет, добавь его в `.gitignore`.")
        print("  3. Отмени добавление в индекс: git restore --staged <имя_файла>")
        print("=" * 70 + "\n")
        sys.exit(1)  # Блокируем коммит (код ошибки 1)

    # Если всё хорошо
    sys.exit(0)


if __name__ == "__main__":
    main()
