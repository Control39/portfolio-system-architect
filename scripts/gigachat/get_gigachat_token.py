#!/usr/bin/env python3
"""Получение GigaChat access token через OAuth"""

import base64
import os
import requests
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🔐 Получение GigaChat Access Token")
print("=" * 80)

# Получаем данные из переменных окружения
client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

print(f"\n📋 Параметры:")
print(f"   Client ID: {client_id}")
print(f"   Client Secret: {client_secret[:20]}...")
print(f"   Auth URL: {auth_url}")
print(f"   Scope: {scope}")
print(f"   Verify SSL: {verify_ssl}")

if not client_id or not client_secret:
    print("\n❌ Ошибка: GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET должны быть настроены в .env")
    sys.exit(1)

# Формируем заголовки для OAuth
auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {
    "scope": scope,
    "grant_type": "client_credentials",
}

print("\n🔒 Отправка запроса к GigaChat OAuth...")
print(f"   URL: {auth_url}")
print(f"   Headers: {headers['Authorization'][:30]}...")

try:
    response = requests.post(auth_url, headers=headers, data=data, timeout=30, verify=verify_ssl)

    print(f"\n✅ Ответ получен: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            print(f"\n🎉 Access Token получен успешно!")
            print(f"   Токен: {access_token[:50]}...")
            print(f"   Длина: {len(access_token)} символов")

            # Выводим в формате для .env
            print(f"\n💡 Для .env файла:")
            print(f"   GIGACHAT_API_KEY={access_token}")

            # Проверяем токен
            print("\n🔍 Проверка токена...")
            api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            api_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-User-ID": "token-validator",
            }

            api_payload = {
                "model": "GigaChat-Latest",
                "messages": [{"role": "user", "content": "Привет"}],
                "temperature": 0.7,
                "max_tokens": 100,
            }

            api_response = requests.post(api_url, json=api_payload, headers=api_headers, timeout=30, verify=verify_ssl)

            if api_response.status_code == 200:
                result = api_response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"   ✅ Tокен работает! Ответ: {content}")
                print("\n" + "=" * 80)
                print("✅ ГОТОВО! Обновите .env файл с новым токеном")
                print("=" * 80)
            else:
                print(f"   ⚠️ Ошибка проверки токена: {api_response.status_code}")
                print(f"   {api_response.text[:200]}")
        else:
            print(f"\n❌ Ошибка: В ответе нет access_token")
            print(f"   Ответ: {response.text}")
            sys.exit(1)
    else:
        print(f"\n❌ Ошибка получения токена: {response.status_code}")
        print(f"   Текст: {response.text}")
        sys.exit(1)

except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
