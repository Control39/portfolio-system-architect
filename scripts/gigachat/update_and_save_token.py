#!/usr/bin/env python3
"""Обновление GigaChat токена и сохранение в .env"""

import os
import sys
from pathlib import Path

# Добавляем src в путь
for p in ["src", str(Path(__file__).parent / "src")]:
    if p not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ";" + p
    if p not in sys.path:
        sys.path.insert(0, p)

from ai.config.token_refresh_service import get_token_refresh_service

# Устанавливаем переменные окружения
os.environ["GIGACHAT_CLIENT_ID"] = "54b03e66-d6b4-4945-aae4-e071d1439347"
os.environ["GIGACHAT_CLIENT_SECRET"] = "b6caf308-8ac8-4caf-b9a8-435568f31658"

# Получаем сервис и токен
service = get_token_refresh_service()
token = service.get_token(force_refresh=True)  # Принудительное обновление

if token:
    print(f"✅ Токен получен (длина: {len(token)})")

    # Сохраняем в .env
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Обновляем или добавляем GIGACHAT_API_KEY
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GIGACHAT_API_KEY="):
                lines[i] = f"GIGACHAT_API_KEY={token}\n"
                updated = True
                break

        if not updated:
            lines.append(f"GIGACHAT_API_KEY={token}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Токен сохранён в {env_path}")

        # Проверка
        from ai.config.config_manager import ConfigManager

        config = ConfigManager("config/ai-config.yaml")
        config_token = config.get_gigachat_token(force_refresh=True)
        print(f"✅ Токен в ConfigManager: {len(config_token)} символов")
else:
    print("❌ Не удалось получить токен")
