#!/usr/bin/env python3
"""Получение GigaChat токена через TokenRefreshService"""

import os
import sys
from pathlib import Path

# Добавляем src в путь
for p in ["src", str(Path(__file__).parent / "src")]:
    if p not in os.environ.get("PYTHONPATH", ""):
        os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + ";" + p
    if p not in sys.path:
        sys.path.insert(0, p)

# Устанавливаем переменные окружения
os.environ["GIGACHAT_CLIENT_ID"] = "54b03e66-d6b4-4945-aae4-e071d1439347"
os.environ["GIGACHAT_CLIENT_SECRET"] = "b6caf308-8ac8-4caf-b9a8-435568f31658"

from ai.config.token_refresh_service import TokenRefreshService, get_token_refresh_service


def main():
    print("=" * 80)
    print("🚀 Запуск TokenRefreshService")
    print("=" * 80)

    # Получаем сервис
    service = get_token_refresh_service()

    # Получаем токен
    token = service.get_token()

    if token:
        print(f"\n✅ Токен получен (длина: {len(token)})")
        print(f"   Первые 20 символов: {token[:20]}...")

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

        # Информация о токене
        info = service.get_token_info()
        print(f"\nℹ Информация о токене:")
        print(f"  Экспирация: {info['time_remaining'] / 60:.1f} минут")

        # Запускаем авто-обновление
        service.start_auto_refresh(interval=60)
        print("\nℹ Auto-refresh запущен (обновление каждые 60 сек)")
        print("   Остановите скрипт с помощью Ctrl+C")

        # Ждём (можно заменить на цикл ожидания)
        try:
            import time

            time.sleep(300)  # 5 минут
        except KeyboardInterrupt:
            print("\n\n⚠ Остановлено пользователем")

        service.stop_auto_refresh()
        print("\n✅ Auto-refresh остановлен")

    else:
        print("\n❌ Не удалось получить токен")
        print("   Проверьте GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET")


if __name__ == "__main__":
    main()
