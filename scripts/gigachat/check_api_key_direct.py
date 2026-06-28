#!/usr/bin/env python3
"""Проверка GIGACHAT_API_KEY напрямую"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GIGACHAT_API_KEY")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

print("=" * 80)
print("🔍 Проверка GIGACHAT_API_KEY")
print("=" * 80)

if not api_key:
    print("❌ GIGACHAT_API_KEY не установлен")
    print("   Используйте GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET для получения токена")
    exit(1)

print(f"\n📋 GIGACHAT_API_KEY:")
print(f"   {api_key[:50]}... (длина: {len(api_key)})")

# Проверяем, является ли это access token или base64 client_id:client_secret
import base64

try:
    decoded = base64.b64decode(api_key).decode("utf-8")
    print(f"\n⚠️  ВНИМАНИЕ: GIGACHAT_API_KEY похож на base64 encoded client_id:client_secret!")
    print(f"   Декодировано: {decoded}")
    print(f"   Это НЕ правильный формат для GigaChat API.")
    print(f"   Правильный формат: Bearer token (JWT)")
except:
    print(f"\n✅ GIGACHAT_API_KEY не в base64 формате (возможно, это access token)")

# Пробуем использовать как access token
url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-User-ID": "api-key-validator",
}

payload = {
    "model": "GigaChat-Latest",
    "messages": [{"role": "user", "content": "Привет"}],
    "temperature": 0.7,
    "max_tokens": 50,
}

print(f"\n🌐 Проверка токена через GigaChat API...")
print(f"   URL: {url}")
print(f"   Verify SSL: {verify_ssl}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

    print(f"\n✅ Ответ получен: {response.status_code}")
    print(f"   Текст: {response.text[:500]}")

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"\n✅ GIGACHAT_API_KEY валиден!")
        print(f"   GigaChat ответил: {content}")
    elif response.status_code == 401:
        print(f"\n❌ GIGACHAT_API_KEY невалиден (401 Unauthorized)!")
    else:
        print(f"\n❌ Ошибка при проверке токена: {response.status_code}")

except Exception as e:
    print(f"\n❌ Ошибка проверки токена: {e}")
    import traceback

    traceback.print_exc()
