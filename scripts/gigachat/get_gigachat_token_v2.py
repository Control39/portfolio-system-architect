#!/usr/bin/env python3
"""Получение GigaChat Access Token с RqUID заголовком"""

import os
import sys
import base64
import requests
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

print("=" * 80)
print("🔐 Получение GigaChat Access Token (с RqUID)")
print("=" * 80)

if not client_id or not client_secret:
    print("❌ GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET должны быть установлены")
    sys.exit(1)

# Генерируем Auth Header
auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

# Генерируем уникальный RqUID
import uuid

rquid = str(uuid.uuid4())

print(f"\n📋 Параметры:")
print(f"   Client ID: {client_id[:20]}...")
print(f"   Auth Header: Basic {encoded_auth[:30]}...")
print(f"   RqUID: {rquid}")
print(f"   Scope: {scope}")
print(f"   Auth URL: {auth_url}")

# Отправляем запрос с правильными заголовками
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": rquid,
}

data = {
    "scope": scope,
    "grant_type": "client_credentials",
}

print(f"\n📤 Отправка запроса...")

try:
    response = requests.post(auth_url, headers=headers, data=data, timeout=30, verify=verify_ssl)

    print(f"\n📥 Ответ:")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            print(f"\n✅ Access Token получен!")
            print(f"   Токен: {access_token[:50]}...")
            print(f"   Длина: {len(access_token)} символов")
            print(f"   Expires in: {token_data.get('expires_in', 'N/A')} секунд")
            print(f"   Scope: {token_data.get('scope', 'N/A')}")

            # Сохраняем в .env
            env_path = Path(".env")
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
            import json

            settings_path = Path(".vscode/settings.json")
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            settings["gigacode.bearerToken"] = access_token

            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

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
                "model": "GigaChat",
                "messages": [{"role": "user", "content": "Привет"}],
                "temperature": 0.7,
                "max_tokens": 50,
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"   ✅ Токен валиден!")
                print(f"   GigaChat ответил: {content}")
            else:
                print(f"   ❌ Ошибка проверки токена: {response.status_code}")
                print(f"   Текст: {response.text[:500]}")

        else:
            print(f"\n❌ В ответе нет access_token")
            print(f"   Ответ: {response.text[:500]}")

    else:
        print(f"\n❌ Ошибка получения токена: {response.status_code}")
        print(f"   Текст: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
