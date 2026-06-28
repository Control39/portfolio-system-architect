#!/usr/bin/env python3
"""Проверка формата GigaChat API ключа"""

import base64
import os

print("=" * 80)
print("📋 Проверка GigaChat API ключа")
print("=" * 80)

# Проверяем, что сейчас в переменной окружения
api_key = os.getenv("GIGACHAT_API_KEY")

print(f"\nТекущий GIGACHAT_API_KEY: {api_key[:30]}...")

# Проверяем формат
try:
    decoded = base64.b64decode(api_key).decode("utf-8")
    print(f"\nДекодировано (base64): {decoded}")
    print(f"Длина декодированного: {len(decoded)} символов")

    # Проверяем, похоже ли на client_id:client_secret
    if ":" in decoded and len(decoded.split(":")) == 2:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: GIGACHAT_API_KEY содержит client_id:client_secret в base64!")
        print("   Это НЕ правильный формат для GigaChat API.")
        print("\n   Правильный формат:")
        print("   - Сначала получить access_token через OAuth (client_id:client_secret)")
        print("   - Затем использовать access_token в GIGACHAT_API_KEY")
        print("\n   Или просто использовать GIGACHAT_CLIENT_ID + GIGACHAT_CLIENT_SECRET")
        print("   и полагаться на ConfigManager.get_gigachat_token()")

        client_id, client_secret = decoded.split(":", 1)
        print(f"\n   Текущий client_id: {client_id}")
        print(f"   Текущий client_secret: {client_secret[:20]}...")

    else:
        print("ℹ️ Ключ похож на правильный access_token")

except Exception as e:
    print(f"Ошибка декодирования: {e}")
    print("   Ключ не в base64 формате")

print("\n" + "=" * 80)
print("💡 РЕКОМЕНДАЦИЯ:")
print("=" * 80)
print("""
1. Удалите GIGACHAT_API_KEY из .env
2. Оставьте только GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET
3. ConfigManager.get_gigachat_token() автоматически получит access_token

ИЛИ:

1. Получите access_token через OAuth (client_id:client_secret)
2. Скопируйте access_token и установите его в GIGACHAT_API_KEY

Скрипт get_gigachat_token.py автоматически получит токен:

```python
from src.ai.config import ConfigManager
config = ConfigManager("agents/cognitive_agent/config/agent-config.yaml")
token = config.get_gigachat_token()
print(f"Access token: {token}")
```
""")
