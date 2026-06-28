#!/usr/bin/env python3
"""Генерация тестов с таймаутом"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/repo")

from src.ai.config.token_refresh_service import TokenRefreshService
from src.ai.gigachat_bridge import GigaMCPBridge, GigaChainSettings
from src.shared.utils import get_config_value
import time


# Проверим токен
async def test_token():
    print("🔄 Проверка токена GigaChat...")
    start = time.time()

    service = TokenRefreshService()
    token = await service.get_token()

    elapsed = time.time() - start
    print(f"✅ Токен получен за {elapsed:.2f} сек, длина: {len(token)}")

    # Проверим валидность (начинается с eyJ)
    if token.startswith("eyJ"):
        print("✅ Токен валидный (JWT формат)")
    else:
        print("❌ Токен не валидный")


asyncio.run(test_token())
