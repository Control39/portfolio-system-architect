#!/usr/bin/env python3
"""Получение GigaChat Access Token через OAuth (простая версия)"""

import os
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем credentials
client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() != "false"

print("=" * 80)
print("🔐 Получение GigaChat Access Token")
print("=" * 80)

# Проверяем credentials
if not client_id or not client_secret:
    print("❌ Ошибка: GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET должны быть установлены")
    sys.exit(1)

print(f"\n📋 Параметры:")
print(f"   Client ID: {client_id[:20]}...")
print(f"   Client Secret: {client_secret[:20]}...")
print(f"   Scope: {scope}")
print(f"   Auth URL: {auth_url}")
print(f"   Verify SSL: {verify_ssl}")

# Генерируем Auth Header
auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

print(f"\n🔒 Отправка запроса к GigaChat OAuth...")
print(f"   URL: {auth_url}")
print(f"   Headers: Basic {encoded_auth[:30]}...")

# Отправляем запрос
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {
    "scope": scope,
    "grant_type": "client_credentials",
}

try:
    response = requests.post(auth_url, headers=headers, data=data, timeout=30, verify=verify_ssl)

    print(f"\n✅ Ответ получен: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            print(f"\n✅ Access Token получен!")
            print(f"   Токен: {access_token[:50]}...")
            print(f"   Длина: {len(access_token)} символов")

            # Сохраняем токен в кэш
            cache_file = Path(".gigacode_token_cache.json")
            cache_data = {
                "token": access_token,
                "expires_at": "1 hour from now",  # Просто для информации
                "created_at": str(Path(__file__).parent),
            }

            import json

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

            print(f"   ✅ Токен сохранён в {cache_file}")

            # Обновляем .vscode/settings.json
            settings_file = Path(".vscode/settings.json")
            if settings_file.exists():
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = f.read()

                # Заменяем токен
                import re

                new_settings = re.sub(
                    r'"gigacode\.bearerToken"\s*:\s*"[^"]*"', f'"gigacode.bearerToken": "{access_token}"', settings
                )

                with open(settings_file, "w", encoding="utf-8") as f:
                    f.write(new_settings)

                print(f"   ✅ Токен обновлён в .vscode/settings.json")

            # Обновляем .env файл
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                new_lines = []
                for line in lines:
                    if line.startswith("GIGACHAT_API_KEY=") or line.startswith("#GIGACHAT_API_KEY="):
                        new_lines.append(f"GIGACHAT_API_KEY={access_token}\n")
                    else:
                        new_lines.append(line)

                with open(env_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

                print(f"   ✅ Токен обновлён в .env")

            print(f"\n🎉 Готово! Токен получен и сохранён.")

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

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30, verify=verify_ssl)

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"   ✅ Токен валиден!")
                    print(f"   GigaChat ответил: {content}")
                elif response.status_code == 401:
                    print(f"   ❌ Токен невалиден (401 Unauthorized)!")
                else:
                    print(f"   ❌ Ошибка при проверке токена: {response.status_code}")
                    print(f"   Текст: {response.text[:200]}")

            except Exception as e:
                print(f"   ⚠️  Ошибка проверки токена: {e}")

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
