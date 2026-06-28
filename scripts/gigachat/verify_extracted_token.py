#!/usr/bin/env python3
"""Проверка извлечённого токена с GigaChat API"""

import os
import requests
import urllib3
from pathlib import Path

# Отключаем предупреждения о непроверенных запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Читаем токен
token_path = "extracted_token.txt"
if not Path(token_path).exists():
    print(f"❌ Файл {token_path} не найден!")
    exit(1)

with open(token_path, "r", encoding="utf-8") as f:
    token = f.read().strip()

print("=" * 80)
print("🔐 Проверка извлечённого токена")
print("=" * 80)
print(f"\nТокен из {token_path}")
print(f"Длина: {len(token)} символов")
print(f"Первые 100: {token[:100]}...")

# Проверяем токен через GigaChat API
print("\n🌐 Проверка токена через GigaChat API...")

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

# Отключаем SSL verification для корпоративных сетей
verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "false"
print(f"SSL verification: {verify_ssl}")

try:
    response = requests.post(
        url, json=payload, headers=headers, timeout=30, verify=False
    )  # Всегда отключаем для JWE токенов

    print(f"\nСтатус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"\n✅ Токен валиден!")
        print(f"GigaChat ответил: {content}")

        # Обновляем .env файл
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            found = False

            for line in lines:
                if line.startswith("GIGACHAT_API_KEY=") or line.startswith("#GIGACHAT_API_KEY="):
                    new_lines.append(f"GIGACHAT_API_KEY={token}\n")
                    found = True
                else:
                    new_lines.append(line)

            if not found:
                new_lines.append(f"\nGIGACHAT_API_KEY={token}\n")

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            print(f"\n✅ Файл .env обновлён!")
            print(f"Теперь можно запустить генерацию тестов:")
            print(f"   python run_test_generation.py")
    elif response.status_code == 401:
        print(f"\n❌ Токен невалиден (401 Unauthorized)!")
        print(f"Возможные причины:")
        print(f"  - Токен истёк")
        print(f"  - Токен неверный")
        print(f"  - Токен зашифрован (JWE) и требует расшифровки")
    else:
        print(f"\n❌ Ошибка при проверке токена: {response.status_code}")

except Exception as e:
    print(f"\n❌ Ошибка проверки токена: {e}")
    import traceback

    traceback.print_exc()
