#!/usr/bin/env python3
"""Получение токена с детальной отладкой"""

import os
import sys
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Устанавливаем переменные окружения
client_id = "54b03e66-d6b4-4945-aae4-e071d1439347"
client_secret = "b6caf308-8ac8-4caf-b9a8-435568f31658"
scope = "GIGACHAT_API_PERS"
auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
verify_ssl = False  # Отключаем SSL для корпоративных сетей

# Генерируем Auth Header
auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

print("=" * 80)
print("🔐 Получение GigaChat Access Token с детальной отладкой")
print("=" * 80)

print(f"\n📋 Данные:")
print(f"   Client ID: {client_id}")
print(f"   Client Secret: {client_secret}")
print(f"   Scope: {scope}")
print(f"   Auth URL: {auth_url}")
print(f"   Verify SSL: {verify_ssl}")

print(f"\n🔒 Auth Header:")
print(f"   {encoded_auth}")

# Создаём сессию с retry стратегией
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# Подготовка запроса
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {
    "scope": scope,
    "grant_type": "client_credentials",
}

print(f"\n📤 Отправка запроса...")

try:
    response = session.post(auth_url, headers=headers, data=data, timeout=30, verify=verify_ssl)

    print(f"\n📥 Ответ:")
    print(f"   Status: {response.status_code}")
    print(f"   Headers:")
    for key, value in response.headers.items():
        print(f"      {key}: {value}")

    # Пытаемся получить тело ответа
    try:
        json_response = response.json()
        print(f"   Body (JSON): {json_response}")

        if response.status_code == 200:
            access_token = json_response.get("access_token")
            if access_token:
                print(f"\n✅ Access Token получен!")
                print(f"   Токен: {access_token[:50]}...")
                print(f"   Длина: {len(access_token)}")

                # Сохраняем в .env
                env_path = ".env"
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    if line.startswith("GIGACHAT_API_KEY="):
                        new_lines.append(f"GIGACHAT_API_KEY={access_token}\n")
                    else:
                        new_lines.append(line)

                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

                print(f"   ✅ Токен сохранён в .env")

                # Обновляем .vscode/settings.json
                import re

                settings_path = ".vscode/settings.json"
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = f.read()

                new_settings = re.sub(
                    r'"gigacode\.bearerToken"\s*:\s*"[^"]*"', f'"gigacode.bearerToken": "{access_token}"', settings
                )

                with open(settings_path, "w", encoding="utf-8") as f:
                    f.write(new_settings)

                print(f"   ✅ Токен сохранён в .vscode/settings.json")

                # Проверяем токен
                print(f"\n🌐 Проверка токена через GigaChat API...")
                url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-User-ID": "token-validator",
                }

                payload = {
                    "model": "GigaChat-Latest",
                    "messages": [{"role": "user", "content": "Привет"}],
                    "temperature": 0.7,
                    "max_tokens": 50,
                }

                response = session.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"   ✅ Токен валиден!")
                    print(f"   GigaChat ответил: {content}")
                else:
                    print(f"   ❌ Ошибка проверки токена: {response.status_code}")
                    print(f"   Текст: {response.text[:500]}")

        else:
            print(f"\n❌ Ошибка: {response.status_code}")
            print(f"   Текст: {response.text[:500]}")

    except requests.exceptions.JSONDecodeError:
        print(f"   Body (текст): {response.text[:500]}")
        print(f"   ❌ Не удалось декодировать ответ как JSON")

except requests.exceptions.RequestException as e:
    print(f"\n❌ Ошибка запроса: {e}")
    import traceback

    traceback.print_exc()
