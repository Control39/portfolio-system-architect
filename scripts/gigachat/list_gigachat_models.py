#!/usr/bin/env python3
"""Получение списка доступных моделей GigaChat"""

import os
import sys
import json
import base64
import requests
import uuid

from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("📋 Получение списка доступных моделей GigaChat")
print("=" * 80)

# Получаем токен
client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

if not client_id or not client_secret:
    print("❌ client_id и client_secret не настроены")
    sys.exit(1)

auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
scope = "GIGACHAT_API_PERS"

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": str(uuid.uuid4()),
}

data = {"scope": scope, "grant_type": "client_credentials"}

verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"

print(" получаем токен...")
response = requests.post(auth_url, headers=headers, data=data, timeout=10, verify=verify_ssl)

if response.status_code != 200:
    print(f"❌ Ошибка получения токена: {response.status_code}")
    print(f"Текст: {response.text}")
    sys.exit(1)

token_data = response.json()
access_token = token_data.get("access_token")

if not access_token:
    print("❌ В ответе нет access_token")
    sys.exit(1)

print(f"✅ Токен получен: {access_token[:50]}...")

# Получаем список моделей
# GigaChat API не имеет endpoint для listing models, но мы можем проверить документацию
# Или попробовать известные имена моделей

known_models = [
    "GigaChat",
    "GigaChat-Pro",
    "GigaChat-Max",
    "GigaChat-Lite",
    "GigaChat-Latest",
    "gigachat",
    "gigachat-pro",
    "gigachat-max",
    "gigachat-lite",
    "gigachat-latest",
]

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

print("\n🔍 Проверка моделей...")
print("-" * 80)

for model in known_models:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Привет"}],
        "temperature": 0.7,
        "max_tokens": 10,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ {model:30s} - РАБОТАЕТ!")
        else:
            print(f"❌ {model:30s} - {response.status_code}")

    except Exception as e:
        print(f"❌ {model:30s} - Ошибка: {e}")

print("-" * 80)

# Проверяем документацию GigaChat
print("\nℹ️  Документация GigaChat API:")
print("   https://developers.sber.ru/docs/ru/gigachat/api/")
