#!/usr/bin/env python3
"""
Обновляет .vscode/settings.json с актуальным GigaChat Access Token

⚠️ Этот скрипт обновляет локальные настройки VS Code.
Токен будет действителен 30 минут.
"""

import json
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта get_token
from get_token import get_valid_token

# Путь к .vscode в корне проекта (абсолютный)
VSCODE_SETTINGS = Path(r"C:\repo\.vscode\settings.json")


def update_vscode_settings(access_token: str):
    """Обновляет настройки VS Code с новым токеном"""

    # Создаем .vscode если не существует
    VSCODE_SETTINGS.parent.mkdir(exist_ok=True)

    # Загружаем текущие настройки
    settings = {}
    if VSCODE_SETTINGS.exists():
        with open(VSCODE_SETTINGS, encoding="utf-8") as f:
            settings = json.load(f)

    # Обновляем настройки Gigacode
    settings["gigacode.apiEndpoint"] = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    settings["gigacode.authorizationHeader"] = f"Bearer {access_token}"
    settings["gigacode.accessToken"] = access_token
    settings["gigacode.maxContextTokens"] = 4096
    settings["gigacode.maxResponseTokens"] = 2048
    settings["gigacode.enableWorkspaceContext"] = False

    # Сохраняем
    with open(VSCODE_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    print(f"✅ Обновлен файл: {VSCODE_SETTINGS}")


def main():
    print("=" * 60)
    print("Обновление токена для VS Code Gigacode Extension")
    print("=" * 60)

    try:
        # Получаем актуальный токен
        access_token = get_valid_token()

        # Обновляем настройки VS Code
        update_vscode_settings(access_token)

        print("\n" + "=" * 60)
        print("✅ Готово!")
        print("=" * 60)
        print("\nТеперь перезагрузите VS Code:")
        print("  Ctrl+Shift+P → 'Developer: Reload Window'")
        print("\nТокен действителен 30 минут.")
        print("Запустите этот скрипт снова для обновления.")

        return 0

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
