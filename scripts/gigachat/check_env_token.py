#!/usr/bin/env python3
"""Проверка токена из .env"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Получаем токен из .env
api_key = os.getenv("GIGACHAT_API_KEY")

print("=" * 80)
print("🔐 Проверка токена из .env")
print("=" * 80)

if not api_key:
    print("❌ GIGACHAT_API_KEY не установлен")
    exit(1)

print(f"\n📋 Токен:")
print(f"   Длина: {len(api_key)} символов")
print(f"   Первые 50: {api_key[:50]}...")

# Проверяем токен через GigaChat API
url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-User-ID": "token-validator",
}

payload = {
    "model": "GigaChat-Latest",
    "messages": [{"role": "user", "content": "Привет"}],
    "temperature": 0.7,
    "max_tokens": 50,
}

verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"
print(f"\n🌐 Проверка токена через GigaChat API...")
print(f"   SSL verification: {verify_ssl}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)

    print(f"\n✅ Ответ получен: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"\n✅ Токен валиден!")
        print(f"   GigaChat ответил: {content}")
        print(f"\n🎉 Готово! Можно приступать к генерации тестов:")
        print(f"   python run_test_generation.py")
    elif response.status_code == 401:
        print(f"\n❌ Токен невалиден (401 Unauthorized)!")
        print(f"   Текст: {response.text[:500]}")
    else:
        print(f"\n❌ Ошибка при проверке токена: {response.status_code}")
        print(f"   Текст: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ Ошибка проверки токена: {e}")
    import traceback

    traceback.print_exc()
