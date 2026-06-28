#!/usr/bin/env python3
"""Демонстрация авто-обновления GigaChat токенов."""

import os
import time
import uuid
from pathlib import Path

# Добавляем src в путь
sys_path_added = False
for p in ["src", "C:/repo/src"]:
    if p not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ";" + p
        sys_path_added = True

import sys

if sys_path_added:
    sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai.config.config_manager import ConfigManager
from ai.config.token_refresh_service import TokenRefreshService


def demo_basic_refresh():
    """Демонстрация базового обновления токена."""
    print("\n" + "=" * 80)
    print("Demo 1: Basic Token Refresh")
    print("=" * 80)

    service = TokenRefreshService()
    print("✓ TokenRefreshService создан")

    # Первый запрос
    token1 = service.get_token()
    if token1:
        print(f"✓ Токен получен (длина: {len(token1)})")
        info1 = service.get_token_info()
        print(f"  Экспирация: {info1['time_remaining']:.1f} сек")

        # Ждём немного (имитация времени)
        time.sleep(1)

        # Второй запрос (должен вернуть кэшированный)
        token2 = service.get_token()
        print(f"✓ Второй запрос (кэш): {'сработал' if token1 == token2 else 'новый токен'}")
    else:
        print("❌ Не удалось получить токен")


def demo_auto_refresh():
    """Демонстрация авто-обновления в фоновом потоке."""
    print("\n" + "=" * 80)
    print("Demo 2: Auto Refresh (Background Thread)")
    print("=" * 80)

    service = TokenRefreshService()

    # Запускаем авто-обновление каждые 10 секунд
    service.start_auto_refresh(interval=10)
    print("✓ Auto-refresh запущен (interval=10s)")

    # Проверяем токены каждые 3 секунды
    for i in range(5):
        token = service.get_token()
        info = service.get_token_info()

        if token:
            print(f"[{i+1}] Токен активен (осталось: {info['time_remaining']:.0f} сек)")
        else:
            print(f"[{i+1}] ❌ Токен недоступен")

        time.sleep(3)

    # Останавливаем
    service.stop_auto_refresh()
    print("✓ Auto-refresh остановлен")


def demo_with_config_manager():
    """Демонстрация интеграции с ConfigManager."""
    print("\n" + "=" * 80)
    print("Demo 3: ConfigManager Integration")
    print("=" * 80)

    # Загружаем конфигурацию
    config_path = "config/ai-config.yaml"
    if not Path(config_path).exists():
        print(f"⚠ Конфигурация не найдена: {config_path}")
        print("   Пропускаем тест ConfigManager")
        return

    config_manager = ConfigManager(config_path, auto_reload=False)
    print("✓ ConfigManager загружен")

    # Получаем токен через ConfigManager
    token = config_manager.get_gigachat_token()
    if token:
        print(f"✓ Токен получен через ConfigManager (длина: {len(token)})")
    else:
        print("❌ Не удалось получить токен через ConfigManager")

    # Запускаем авто-обновление
    config_manager.start_token_auto_refresh(interval=60)
    print("✓ Auto-refresh в ConfigManager запущен")

    # Проверяем токен
    token2 = config_manager.get_gigachat_token()
    print(f"✓ Второй запрос: {'успешен' if token2 else 'неудачен'}")

    # Останавливаем
    config_manager.stop_token_auto_refresh()
    print("✓ Auto-refresh остановлен")


def demo_rquid_headers():
    """Демонстрация работы с RqUID заголовками."""
    print("\n" + "=" * 80)
    print("Demo 4: RqUID Header Verification")
    print("=" * 80)

    service = TokenRefreshService()

    # Внутренний метод генерирует RqUID
    rquid = service._generate_rquid()
    print(f"✓ RqUID сгенерирован: {rquid}")
    print(f"  Формат UUID: {uuid.UUID(rquid)}")
    print(f"  Длина: {len(rquid)} символов")


def main():
    """Запуск всех демонстраций."""
    print("=" * 80)
    print("🚀 GigaChat Auto-Refresh Demonstration")
    print("=" * 80)

    # Проверяем переменные окружения
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("\n⚠ ВНИМАНИЕ: GIGACHAT_CLIENT_ID или GIGACHAT_CLIENT_SECRET не настроены")
        print("   Установите переменные окружения перед запуском:")
        print('   $env:GIGACHAT_CLIENT_ID="..."')
        print('   $env:GIGACHAT_CLIENT_SECRET="..."')
        return

    print(f"\n✓ GIGACHAT_CLIENT_ID настроен: {client_id[:8]}...{client_id[-4:] if len(client_id) > 12 else ''}")
    print(f"✓ GIGACHAT_CLIENT_SECRET настроен: {'*' * 8}...{'*' * 4}")

    try:
        demo_rquid_headers()
        demo_basic_refresh()
        demo_auto_refresh()
        demo_with_config_manager()

        print("\n" + "=" * 80)
        print("✅ Все демонстрации завершены")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
