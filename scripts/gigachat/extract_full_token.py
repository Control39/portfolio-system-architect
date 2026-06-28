#!/usr/bin/env python3
"""Восстановление правильного JSON из .vscode/settings.json"""

import re

settings_path = ".vscode/settings.json"

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

print("Полный файл:")
print(content)
print()

# Извлекаем токен из комментария
# Токен находится после " Получает новый Access Token от GigaChat\n"
pattern = r'"gigacode\.bearerToken"\s*:\s*""\s*Получает кэшированный токен.*?\n\s*" "\s*Получает новый Access Token от GigaChat\n\s*" ([^"]+)'
match = re.search(pattern, content, re.DOTALL)

if match:
    token = match.group(1)
    print(f"✅ Токен извлечён из комментария!")
    print(f"   Длина: {len(token)} символов")
    print(f"   Первые 100: {token[:100]}...")

    # Сохраняем токен во временный файл
    with open("extracted_token.txt", "w", encoding="utf-8") as f:
        f.write(token)
    print(f"   ✅ Токен сохранён в extracted_token.txt")

    # Пытаемся найти остальные настройки
    settings_pattern = r'("gigacode\.[^"]+"\s*:\s*[^,]+),?\n'
    settings = re.findall(settings_pattern, content)
    print(f"\nНайдено настроек: {len(settings)}")
    for s in settings:
        print(f"  {s.strip()}")
else:
    print("❌ Токен не найден!")
