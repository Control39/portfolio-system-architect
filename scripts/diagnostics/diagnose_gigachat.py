#!/usr/bin/env python3
"""Диагностика проблемы с GigaChat API"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🔍 Диагностика GigaChat API")
print("=" * 80)

# Проверка переменных окружения
print("\n📋 Переменные окружения:")
print(f"   GIGACHAT_API_KEY: {os.getenv('GIGACHAT_API_KEY', 'НЕ НАСТРОЕН')[:30]}...")
print(f"   GIGACHAT_CLIENT_ID: {os.getenv('GIGACHAT_CLIENT_ID', 'НЕ НАСТРОЕН')[:30]}...")
print(f"   GIGACHAT_CLIENT_SECRET: {os.getenv('GIGACHAT_CLIENT_SECRET', 'НЕ НАСТРОЕН')[:30]}...")

# Проверка загрузки конфига
print("\n📦 Загрузка конфигурации...")
try:
    from src.ai.config import ConfigManager

    config_path = "agents/cognitive_agent/config/agent-config.yaml"
    config = ConfigManager(config_path=config_path)

    token = config.get_gigachat_token()

    if token:
        print(f"   ✅ Токен загружен: {token[:30]}...")
        print(f"   Длина токена: {len(token)} символов")

        # Проверка формата
        import base64

        try:
            # Пробуем декодировать как base64
            decoded = base64.b64decode(token).decode("utf-8")
            print(f"   ⚠️ Токен в base64 формате (декодировано: {decoded[:50]}...)")
        except:
            print(f"   ℹ️ Токен не в base64 формате")

    else:
        print("   ❌ Токен не загружен!")

except Exception as e:
    print(f"   ❌ Ошибка: {e}")

# Попытка прямого запроса к GigaChat
print("\n🌐 Прямой запрос к GigaChat API...")


async def direct_test():
    """Прямой запрос к GigaChat без промежуточных слоёв"""
    try:
        import base64
        import os
        import requests

        # Получаем токен напрямую
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

        if client_id and client_secret:
            print("   Используем client_id/client_secret для получения токена...")

            auth_string = f"{client_id}:{client_secret}"
            encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": str(__import__("uuid").uuid4()),
            }

            data = {"scope": "GIGACHAT_API_PERS", "grant_type": "client_credentials"}
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            # Учитываем настройку GIGACHAT_VERIFY_SSL для корпоративных сетей
            verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"
            print(f"   SSL verification: {verify_ssl}")
            response = requests.post(auth_url, headers=headers, data=data, timeout=10, verify=verify_ssl)

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")

                if access_token:
                    print(f"   ✅ Новый токен получен!")
                    print(f"   Токен: {access_token[:50]}...")

                    # Проверяем токен
                    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "X-User-ID": "diagnostic-agent",
                    }

                    payload = {
                        "model": "GigaChat",
                        "messages": [{"role": "user", "content": "Привет"}],
                        "temperature": 0.7,
                        "max_tokens": 100,
                    }

                    verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"
                    response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        print(f"   ✅ GigaChat ответил: {content}")
                        return True
                    else:
                        print(f"   ❌ Ошибка ответа: {response.status_code}")
                        print(f"   Текст: {response.text[:200]}")
                        return False
                else:
                    print("   ❌ В ответе нет access_token")
                    return False
            else:
                print(f"   ❌ Ошибка получения токена: {response.status_code}")
                print(f"   Текст: {response.text}")
                return False
        else:
            print("   ⚠️ client_id и client_secret не настроены")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return False


result = asyncio.run(direct_test())

# Результаты
print("\n" + "=" * 80)
print("📊 РЕЗУЛЬТАТЫ")
print("=" * 80)

if result:
    print("\n✅ GigaChat работает! Можно приступать к генерации тестов.")
else:
    print("\n❌ GigaChat не работает. Проверьте:")
    print("   1. Правильность client_id и client_secret")
    print("   2. Доступность GigaChat API (https://ngw.devices.sberbank.ru:9443)")
    print("   3. Время жизни токена (возможно, нужно обновить)")
    print("\n💡 Для получения нового ключа:")
    print("   - Зарегистрируйтесь на SberCloud")
    print("   - Перейдите в GigaChat API")
    print("   - Получите client_id и client_secret")
    print("   - Обновите их в .env файле")
