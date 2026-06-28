#!/usr/bin/env python3
"""Установка токена из .vscode/settings.json в GIGACHAT_API_KEY"""

import json
import re
from pathlib import Path

# Читаем токен из .vscode/settings.json
settings_path = Path(".vscode/settings.json")

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# Извлекаем токен из комментария (как в предыдущих диагностиках)
pattern = r'"gigacode\.bearerToken"\s*:\s*""\s*Получает кэшированный токен.*?\n\s*" "\s*Получает новый Access Token от GigaChat\n\s*" ([^"]+)'
match = re.search(pattern, content, re.DOTALL)

if match:
    token = match.group(1)
    print(f"✅ Токен извлечён из .vscode/settings.json!")
    print(f"   Длина: {len(token)} символов")
    print(f"   Первые 100: {token[:100]}...")

    # Обновляем .env файл
    env_path = Path(".env")

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("GIGACHAT_API_KEY="):
            new_lines.append(f"GIGACHAT_API_KEY={token}\n")
        else:
            new_lines.append(line)

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"   ✅ Токен установлен в .env")

    # Проверяем токен
    print(f"\n🌐 Проверка токена через GigaChat API...")
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

    import os

    verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)

        print(f"\n✅ Ответ получен: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"   ✅ Токен валиден!")
            print(f"   GigaChat ответил: {content}")
        elif response.status_code == 401:
            print(f"   ❌ Токен невалиден (401 Unauthorized) - токен истёк!")
            print(f"   Текст: {response.text[:500]}")
        else:
            print(f"   ❌ Ошибка при проверке токена: {response.status_code}")
            print(f"   Текст: {response.text[:500]}")

    except Exception as e:
        print(f"   ⚠️  Ошибка проверки токена: {e}")

else:
    print(f"❌ Токен не найден в .vscode/settings.json!")
