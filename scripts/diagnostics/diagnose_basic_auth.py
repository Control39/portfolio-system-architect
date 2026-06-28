#!/usr/bin/env python3
"""Диагностика Basic auth header"""

import base64
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("GIGACHAT_CLIENT_ID")
client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

print("=" * 80)
print("🔍 Диагностика Basic auth header")
print("=" * 80)

print(f"\n📋 Входные данные:")
print(f"   Client ID: {client_id}")
print(f"   Client Secret: {client_secret}")

# Формируем auth string
auth_string = f"{client_id}:{client_secret}"
print(f"\n🔒 Auth string: {auth_string}")
print(f"   Длина: {len(auth_string)}")

# Кодируем в base64
encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
print(f"\nEncoded auth: {encoded_auth}")
print(f"   Длина: {len(encoded_auth)}")

# Декодируем обратно для проверки
decoded_auth = base64.b64decode(encoded_auth).decode("utf-8")
print(f"\nDecoded auth: {decoded_auth}")

# Проверяем, что декодировано правильно
if decoded_auth == auth_string:
    print("✅ Кодирование/декодирование верное!")
else:
    print("❌ Ошибка кодирования!")

# Проверяем заголовок
print(f"\n📌 Заголовок Authorization:")
print(f"   Basic {encoded_auth}")

# Проверяем на наличие лишних символов
import re

if re.match(r"^[A-Za-z0-9+/]+=*$", encoded_auth):
    print("✅ Заголовок содержит только допустимые символы")
else:
    print("⚠️  Заголовок содержит недопустимые символы!")
