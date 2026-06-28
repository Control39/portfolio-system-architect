#!/usr/bin/env python3
"""Диагностика ConfigManager.get_gigachat_token()"""

import sys
import os
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Устанавливаем переменные окружения
os.environ["GIGACHAT_CLIENT_ID"] = "54b03e66-d6b4-4945-aae4-e071d1439347"
os.environ["GIGACHAT_CLIENT_SECRET"] = "b6caf308-8ac8-4caf-b9a8-435568f31658"
os.environ["GIGACHAT_SCOPE"] = "GIGACHAT_API_PERS"
os.environ["GIGACHAT_AUTH_URL"] = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
os.environ["GIGACHAT_VERIFY_SSL"] = "false"
os.environ["GIGACHAT_API_KEY"] = ""  # Пустой, чтобы сделать OAuth запрос

print("=" * 80)
print("🔍 Диагностика ConfigManager.get_gigachat_token()")
print("=" * 80)

print(f"\n📋 Переменные окружения:")
print(f"   GIGACHAT_CLIENT_ID: {os.environ.get('GIGACHAT_CLIENT_ID')}")
print(f"   GIGACHAT_CLIENT_SECRET: {os.environ.get('GIGACHAT_CLIENT_SECRET')[:20]}...")
print(f"   GIGACHAT_API_KEY: {os.environ.get('GIGACHAT_API_KEY', 'НЕТ')}")
print(f"   GIGACHAT_AUTH_URL: {os.environ.get('GIGACHAT_AUTH_URL')}")
print(f"   GIGACHAT_VERIFY_SSL: {os.environ.get('GIGACHAT_VERIFY_SSL')}")

# Загружаем ConfigManager
try:
    from src.ai.config import ConfigManager

    print(f"\n📦 Загрузка ConfigManager...")
    config = ConfigManager("agents/cognitive_agent/config/agent-config.yaml")
    print(f"   ✅ ConfigManager загружен")

    print(f"\n🔐 Получение токена через ConfigManager.get_gigachat_token()...")
    token = config.get_gigachat_token()

    print(f"\n📋 Полученный токен:")
    print(f"   Токен: {token}")
    print(f"   Длина: {len(token) if token else 0}")

    if token:
        # Проверяем, является ли это access token
        import base64

        try:
            decoded = base64.b64decode(token).decode("utf-8")
            if ":" in decoded:
                print(f"\n⚠️  ВНИМАНИЕ: Токен похож на base64 encoded client_id:client_secret!")
                print(f"   Декодировано: {decoded}")
            else:
                print(f"\n✅ Токен не в base64 формате (возможно, это access token)")
        except:
            print(f"\n✅ Токен не в base64 формате (возможно, это access token)")

        # Проверяем токен через GigaChat API
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

        verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

            print(f"\n✅ Ответ получен: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"   ✅ Токен валиден!")
                print(f"   GigaChat ответил: {content}")
            elif response.status_code == 401:
                print(f"   ❌ Токен невалиден (401 Unauthorized)!")
            else:
                print(f"   ❌ Ошибка при проверке токена: {response.status_code}")
                print(f"   Текст: {response.text[:500]}")

        except Exception as e:
            print(f"   ⚠️  Ошибка проверки токена: {e}")

except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
