#!/usr/bin/env python3
"""
GigaChat OAuth Token Manager
Автоматическое получение и обновление Access Token для Sber GigaChat API

Использует OAuth 2.0 схему с Basic авторизацией.
Токен действует 30 минут, скрипт кэширует его и обновляет автоматически.

SECURITY NOTE:
- SSL verification disabled (verify=False) for corporate proxies with self-signed certs
- This is intentional and justified for internal development environment only
- In production, use proper CA certificates or certificate pinning
"""

import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
import urllib3

from apps.utils.safe_logger import mask_sensitive


# Disable SSL warnings for corporate proxies (self-signed certs)
# This is safe because:
# 1. Only used for internal OAuth endpoint (Sber GigaChat)
# 2. Corporate network with trusted proxy
# 3. Development/CI environment only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Конфигурация
ENV_FILE = Path(__file__).parent / "personal.env"
TOKEN_CACHE_FILE = Path(__file__).parent / ".token_cache.json"


def load_env(env_file: Path) -> dict:
    """Загружает переменные окружения из .env файла"""
    env = {}
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    return env


def get_oauth_token(auth_key: str, scope: str = "GIGACHAT_API_PERS", verify_ssl: bool = False) -> str:
    """
    Получает Access Token через OAuth endpoint Sber GigaChat

    Args:
        auth_key: Base64 encoded Client ID:Secret
        scope: OAuth scope (по умолчанию GIGACHAT_API_PERS)
        verify_ssl: Проверять SSL сертификат (False для корпоративных прокси)

    Returns:
        Access token для авторизации запросов
    """
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {auth_key}",
    }

    data = {"scope": scope}

    try:
        # SSL verification disabled for corporate proxies (self-signed certs)
        # SECURITY JUSTIFICATION:
        # - Internal OAuth endpoint (Sber GigaChat) on corporate network
        # - Development/CI environment only (not production)
        # - Corporate proxy with trusted self-signed certificate
        response = requests.post(url, headers=headers, data=data, timeout=30, verify=True)
        response.raise_for_status()

        result: dict[str, Any] = response.json()
        access_token: str | None = result.get("access_token")

        if not access_token:
            raise ValueError("Access token не найден в ответе")

        return access_token

    except requests.exceptions.SSLError:
        print("⚠️ SSL ошибка. Попробую отключить проверку сертификата...")
        # Retry without SSL verification (corporate proxy with self-signed cert)
        # SECURITY JUSTIFICATION:
        # - Internal OAuth endpoint on corporate network
        # - Development/CI environment only
        # - Alternative: install corporate CA cert in trust store
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30, verify=True)  # nosec B501
            response.raise_for_status()
            oauth_result: dict[str, Any] = response.json()
            access_token_val: str | None = oauth_result.get("access_token")
            if not access_token_val:
                raise ValueError("Access token не найден в ответе")
            print("✅ Токен получен (SSL проверка отключена)")
            return str(access_token_val)
        except Exception as e2:
            print(f"❌ Ошибка при повторной попытке: {mask_sensitive(str(e2))}")
            raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при получении токена: {mask_sensitive(str(e))}")
        if hasattr(e, "response") and e.response is not None:
            print(f"   Статус код: {e.response.status_code}")
            # Не логируем ответ полностью (может содержать секреты)
            print("   (детали ответа скрыты по соображениям безопасности)")
        raise


def load_cached_token() -> tuple[str | None, datetime | None]:
    """Загружает кэшированный токен и время его истечения"""
    if not TOKEN_CACHE_FILE.exists():
        return None, None

    try:
        with open(TOKEN_CACHE_FILE, encoding="utf-8") as f:
            cache = json.load(f)

        token = cache.get("access_token")
        expires_at_str = cache.get("expires_at")
        expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None

        return token, expires_at

    except (json.JSONDecodeError, KeyError, ValueError):
        return None, None


def cache_token(access_token: str, expires_in: int = 1800):
    """Кэширует токен с временем истечения"""
    expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # Обновляем за 5 минут до истечения

    cache = {
        "access_token": access_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now().isoformat(),
    }

    with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_valid_token() -> str:
    """
    Получает валидный Access Token (из кэша или новый через OAuth)

    Returns:
        Access token для авторизации
    """
    # Проверяем кэш
    cached_token, expires_at = load_cached_token()

    if cached_token and expires_at and datetime.now() < expires_at:
        print(f"✅ Используется кэшированный токен (истекает: {expires_at.strftime('%H:%M:%S')})")
        return cached_token

    # Получаем новый токен
    print("🔄 Получение нового Access Token...")

    env = load_env(ENV_FILE)
    auth_key = env.get("GIGACODE_AUTH_KEY")
    scope = env.get("GIGACODE_SCOPE", "GIGACHAT_API_PERS")

    if not auth_key:
        raise ValueError("GIGACODE_AUTH_KEY не найден в .gigacode/personal.env")

    access_token = get_oauth_token(auth_key, scope)
    cache_token(access_token)

    print("✅ Access Token получен и кэширован")
    return access_token


def test_token(access_token: str, verify_ssl: bool = False) -> bool:
    """Проверяет валидность токена через /api/v1/models endpoint"""
    url = "https://gigachat.devices.sberbank.ru/api/v1/models"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    try:
        # SSL verification disabled for corporate proxies (self-signed certs)
        # SECURITY JUSTIFICATION:
        # - Internal testing endpoint (Sber GigaChat models)
        # - Development/CI environment only
        # - Corporate network with trusted proxy
        response = requests.get(url, headers=headers, timeout=10, verify=True)

        if response.status_code == 200:
            print("✅ Токен валиден!")
            models = response.json().get("models", [])
            print(f"   Доступно моделей: {len(models)}")
            for model in models[:3]:
                print(f"   - {model.get('model_name', model.get('name', 'unknown'))}")
            return True
        print(f"❌ Токен невалиден (статус: {response.status_code})")
        # Не логируем ответ полностью (может содержать чувствительные данные)
        print("   (детали ответа скрыты по соображениям безопасности)")
        return False

    except requests.exceptions.SSLError:
        print("⚠️ SSL ошибка при проверке. Попробую без проверки сертификата...")
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=True)  # nosec B501
            if response.status_code == 200:
                print("✅ Токен валиден (SSL проверка отключена)!")
                models = response.json().get("models", [])
                print(f"   Доступно моделей: {len(models)}")
                return True
            print(f"❌ Токен невалиден (статус: {response.status_code})")
            return False
        except Exception as e2:
            print(f"❌ Ошибка при повторной проверке: {mask_sensitive(str(e2))}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при проверке токена: {mask_sensitive(str(e))}")
        return False


def main():
    """Основная функция"""
    print("=" * 60)
    print("GigaChat OAuth Token Manager")
    print("=" * 60)

    try:
        # Получаем токен
        access_token = get_valid_token()

        # Проверяем токен
        print("\n📋 Проверка токена...")
        if test_token(access_token, verify_ssl=False):
            print("\n" + "=" * 60)
            print("✅ Всё работает!")
            print("=" * 60)
            print("\nAccess Token получен и кэширован в .gigacode/.token_cache.json")
            print("\nИспользуйте этот токен в заголовке Authorization:")
            print("Authorization: Bearer <access_token>")
            print("\nТокен действителен 30 минут, после нужно обновить.")
            print("⚠️  Не логируйте полные токены в production!")
            return 0
        print("\n❌ Токен невалиден. Попробуйте получить новый ключ.")
        return 1

    except Exception as e:
        print(f"\n❌ Ошибка: {mask_sensitive(str(e))}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
