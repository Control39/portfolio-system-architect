#!/usr/bin/env python3
"""Детальная диагностика OAuth запроса к GigaChat"""

import base64
import json
import os
import requests
import sys

from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🔍 Детальная диагностика OAuth запроса")
print("=" * 80)

client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

print(f"\n📋 Текущие настройки:")
print(f"   Client ID: {client_id}")
print(f"   Client Secret: {client_secret[:20]}...")
print(f"   Scope: {scope}")

# Вариант 1: Basic auth + form data (стандартный OAuth2)
print("\n" + "-" * 80)
print("Вариант 1: Basic auth + form data")
print("-" * 80)

auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

headers1 = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}

data1 = {
    "scope": scope,
    "grant_type": "client_credentials",
}

print(f"Headers: {headers1}")
print(f"Data: {data1}")

try:
    response1 = requests.post(auth_url, headers=headers1, data=data1, timeout=30, verify=verify_ssl)
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.text[:500]}")
    print(f"Headers: {dict(response1.headers)}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 2: Basic auth + JSON
print("\n" + "-" * 80)
print("Вариант 2: Basic auth + JSON")
print("-" * 80)

headers2 = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json",
}

data2 = {
    "scope": scope,
    "grant_type": "client_credentials",
}

print(f"Headers: {headers2}")
print(f"Data: {json.dumps(data2, indent=2)}")

try:
    response2 = requests.post(auth_url, headers=headers2, json=data2, timeout=30, verify=verify_ssl)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text[:500]}")
    print(f"Headers: {dict(response2.headers)}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 3: Всё через Authorization header (для GigaChat)
print("\n" + "-" * 80)
print("Вариант 3: Всё в Authorization header")
print("-" * 80)

# GigaChat использует специальный формат: Authorization: GigaChat <token>
# Но для OAuth нужно проверить документацию

headers3 = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

print(f"Headers: {headers3}")

try:
    response3 = requests.post(auth_url, headers=headers3, data=data1, timeout=30, verify=verify_ssl)
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text[:500]}")
    if response3.status_code == 200:
        print("\n✅ Это правильный формат!")
        token_data = response3.json()
        print(f"Access token: {token_data.get('access_token', '')[:50]}...")
except Exception as e:
    print(f"Ошибка: {e}")

print("\n" + "=" * 80)
print("💡 Рекомендации:")
print("=" * 80)
print("""
GigaChat API использует специфичный OAuth2 flow.

Согласно документации GigaChat, для получения access token нужно:
1. Использовать Basic auth с client_id:client_secret (base64 encoded)
2. Отправлять данные в form-data format (application/x-www-form-urlencoded)
3. Заголовок Accept: application/json

Если 400 ошибка, возможно:
- Неверный client_id или client_secret
- Неверный scope
- Проблемы с корпоративным прокси/SSL

Для получения ключа зарегистрируйтесь на SberCloud и получите credentials:
https://developers.sber.ru/docs/ru/gigachat/api/oauth
""")
