#!/usr/bin/env python3
"""Тест валидности GigaChat токена через API."""

import os
import sys
from pathlib import Path

# Добавляем src в путь
for p in ["src", str(Path(__file__).parent / "src")]:
    if p not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ";" + p
    if p not in sys.path:
        sys.path.insert(0, p)

import requests
from ai.config.token_refresh_service import TokenRefreshService, get_token_refresh_service


def test_token_with_api(token: str) -> bool:
    """
    Тестирует токен через GigaChat API.

    Args:
        token: Токен для проверки

    Returns:
        bool: True если токен валиден
    """
    api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "GigaChat-Pro",
        "messages": [{"role": "user", "content": "Привет. Как дела?"}],
        "stream": False,
        "temperature": 0.7,
    }

    try:
        verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() != "false"
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=10,
            verify=verify_ssl,
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"✅ Токен валиден!")
            print(f"   Response: {content}")
            return True
        else:
            print(f"❌ Токен недействителен")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке токена: {e}")
        return False


def main():
    print("=" * 80)
    print("🧪 GigaChat Token Validation Test")
    print("=" * 80)

    # Получаем токен через TokenRefreshService
    service = get_token_refresh_service()
    token = service.get_token()

    if not token:
        print("❌ Не удалось получить токен")
        print("   Проверьте GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET")
        return

    print(f"✓ Токен получен (длина: {len(token)})")
    print(f"   Первые 30 символов: {token[:30]}...")

    # Тестируем через API
    print("\n" + "-" * 80)
    print("Testing token via GigaChat API...")
    print("-" * 80)

    is_valid = test_token_with_api(token)

    if is_valid:
        print("\n" + "=" * 80)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("=" * 80)

    # Информация о токене
    info = service.get_token_info()
    print(f"\nℹ Информация о токене:")
    print(f"  Время истечения: {info['expiry_time']}")
    print(f"  Осталось: {info['time_remaining'] / 60:.1f} минут")


if __name__ == "__main__":
    main()
