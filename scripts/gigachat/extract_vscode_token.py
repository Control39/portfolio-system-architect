#!/usr/bin/env python3
"""Извлечение токена из .vscode/settings.json"""

import json
import os
import sys
from pathlib import Path


def extract_token_from_vscode_settings():
    """Извлекает токен из .vscode/settings.json"""
    settings_path = Path(".vscode/settings.json")

    if not settings_path.exists():
        print("❌ Файл .vscode/settings.json не найден!")
        return None

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Исправляем неправильный JSON (удаляем комментарии и лишние кавычки)
        # Токен может быть закомментирован или в неправильном формате

        # Пытаемся найти токен между кавычками
        import re

        # Паттерн для поиска токена в кавычках
        pattern = r'"gigacode\.bearerToken"\s*:\s*"([^"]*)"'
        matches = re.findall(pattern, content)

        if matches:
            token = matches[0]
            if token:  # Проверяем, что токен не пустой
                print(f"✅ Токен найден в .vscode/settings.json!")
                print(f"   Длина токена: {len(token)} символов")
                print(f"   Первые 50 символов: {token[:50]}...")
                return token
            else:
                print("⚠️ Токен найден, но он пустой!")
                return None

        # Если не нашли в кавычках, пробуем другой паттерн (для многострочных)
        # Паттерн для многострочного комментария
        pattern_multiline = r'"gigacode\.bearerToken"\s*:\s*"([^"]*)"(?:\s*/\*.*?\*/)?'
        matches = re.findall(pattern_multiline, content, re.DOTALL)

        if matches:
            token = matches[0]
            if token:
                print(f"✅ Токен найден (многострочный формат)!")
                print(f"   Длина токена: {len(token)} символов")
                return token

        # Пытаемся найти любой JWT токен в файле
        jwt_pattern = r"([A-Za-z0-9_-]{70,}\.[A-Za-z0-9_-]{70,}\.[A-Za-z0-9_-]{70,})"
        jwt_matches = re.findall(jwt_pattern, content)

        if jwt_matches:
            print(f"✅ Найден JWT токен в файле!")
            token = jwt_matches[0]
            print(f"   Длина токена: {len(token)} символов")
            print(f"   Первые 50 символов: {token[:50]}...")
            return token

        print("❌ Токен не найден в .vscode/settings.json!")
        return None

    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        import traceback

        traceback.print_exc()
        return None


def validate_token(token):
    """Проверяет валидность токена через GigaChat API"""
    if not token:
        print("❌ Невозможно проверить пустой токен!")
        return False

    print("\n🌐 Проверка токена через GigaChat API...")

    try:
        import requests

        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-User-ID": "token-validator",
        }

        payload = {
            "model": "GigaChat-Latest",
            "messages": [{"role": "user", "content": "Привет"}],
            "temperature": 0.7,
            "max_tokens": 50,
        }

        # Отключаем SSL verification для корпоративных сетей
        verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

        print(f"   SSL verification: {verify_ssl}")

        response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"   ✅ Токен валиден!")
            print(f"   GigaChat ответил: {content}")
            return True
        elif response.status_code == 401:
            print(f"   ❌ Токен невалиден (401 Unauthorized)!")
            print(f"   Текст: {response.text[:200]}")
            return False
        else:
            print(f"   ❌ Ошибка при проверке токена: {response.status_code}")
            print(f"   Текст: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка проверки токена: {e}")
        import traceback

        traceback.print_exc()
        return False


def update_env_file(token):
    """Обновляет .env файл с новым токеном"""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Находим строку с GIGACHAT_API_KEY и обновляем её
        new_lines = []
        found = False

        for line in lines:
            if line.startswith("GIGACHAT_API_KEY="):
                # Раскомментируем строку и обновляем токен
                new_lines.append(f"GIGACHAT_API_KEY={token}\n")
                found = True
                print(f"✅ Обновлена строка GIGACHAT_API_KEY в .env")
            else:
                new_lines.append(line)

        # Если строка не найдена, добавляем её
        if not found:
            new_lines.append(f"\nGIGACHAT_API_KEY={token}\n")
            print(f"✅ Добавлена строка GIGACHAT_API_KEY в .env")

        # Записываем обратно
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        print(f"✅ Файл .env обновлён!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при обновлении .env: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("🔑 Извлечение токена из .vscode/settings.json")
    print("=" * 80)

    # Извлекаем токен
    token = extract_token_from_vscode_settings()

    if token:
        # Проверяем токен
        is_valid = validate_token(token)

        if is_valid:
            print("\n" + "=" * 80)
            print("🎉 Токен успешно проверен!")
            print("=" * 80)

            # Обновляем .env файл
            update_env_file(token)

            print("\n💡 Теперь можно запустить генерацию тестов:")
            print("   python run_test_generation.py")
        else:
            print("\n⚠️ Токен невалиден. Попробуйте запустить auto-update-gigacode-token.ps1")
    else:
        print("\n❌ Не удалось извлечь токен. Проверьте .vscode/settings.json")
