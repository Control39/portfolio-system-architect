#!/usr/bin/env python3
"""Проверка OAuth запроса через requests с детальной логификацией"""

import os
import sys
import base64
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

print("=" * 80)
print("🔍 Детальная диагностика OAuth запроса")
print("=" * 80)

# Формируем заголовки
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

print(f"\n📤 Запрос:")
print(f"   URL: {auth_url}")
print(f"   Method: POST")
print(f"   Headers:")
for key, value in headers.items():
    print(f"      {key}: {value[:50]}..." if len(value) > 50 else f"      {key}: {value}")
print(f"   Data:")
for key, value in data.items():
    print(f"      {key}: {value}")
print(f"   Verify SSL: {verify_ssl}")

try:
    response = requests.post(auth_url, headers=headers, data=data, timeout=30, verify=verify_ssl)

    print(f"\n📥 Ответ:")
    print(f"   Status: {response.status_code}")
    print(f"   Headers:")
    for key, value in response.headers.items():
        print(f"      {key}: {value}")
    print(f"   Body:")
    print(f"      {response.text[:500]}")

    if response.status_code == 200:
        print(f"\n✅ Запрос успешен!")
        token_data = response.json()
        print(f"   Response JSON: {token_data}")
    else:
        print(f"\n❌ Запрос неуспешен!")

        # Пробуем парсить ошибку
        try:
            error_data = response.json()
            print(f"   Ошибка JSON: {error_data}")
        except:
            print(f"   Ошибка текст: {response.text}")

except RequestException as e:
    print(f"\n❌ Ошибка запроса: {e}")
    import traceback

    traceback.print_exc()
