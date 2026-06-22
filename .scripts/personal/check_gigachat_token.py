#!/usr/bin/env python3
"""
Скрипт для проверки получения токена GigaChat
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Загружаем переменные окружения из .env
env_path = repo_root / ".env"
if env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(env_path)


def check_gigachat_token():
    """Проверяет возможность получения токена GigaChat"""
    print("🔍 Проверка получения токена GigaChat...")

    try:
        # Импортируем обновленный ConfigManager
        from apps.ai_config_manager.src.ai_config_manager import ConfigManager

        # Проверяем существование файла конфигурации
        config_path = repo_root / "config" / "ai-config.yaml"
        if not config_path.exists():
            print(f"❌ Файл конфигурации не найден: {config_path}")
            print("Создаю минимальный файл конфигурации...")

            # Создаем минимальный файл конфигурации
            config_path.parent.mkdir(parents=True, exist_ok=True)
            minimal_config = {"version": "1.0", "agents": {}, "resources": {}}

            import yaml

            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(minimal_config, f, default_flow_style=False, allow_unicode=True)

        # Создаем ConfigManager
        config_manager = ConfigManager(str(config_path))

        # Пробуем получить токен
        print("🔐 Получение токена GigaChat...")
        token = config_manager.get_gigachat_token()

        if token:
            print("✅ Токен GigaChat успешно получен")
            print(f"📜 Токен (первые 20 символов): {token[:20]}...")
            print(f"📏 Длина токена: {len(token)} символов")
            return True
        else:
            print("❌ Не удалось получить токен GigaChat")
            print("\n💡 Возможные причины:")
            print("   - Не установлены переменные окружения GIGACHAT_CLIENT_ID/GIGACHAT_CLIENT_SECRET")
            print("   - Неверные учетные данные")
            print("   - Проблемы с сетевым подключением к API GigaChat")
            print("   - Проблемы с аутентификацией")
            return False

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Ошибка при получении токена: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_environment_vars():
    """Проверяет переменные окружения, необходимые для GigaChat"""
    print("\n📋 Проверка переменных окружения:")

    required_vars = [
        "GIGACHAT_CLIENT_ID",
        "GIGACHAT_CLIENT_SECRET",
        "GIGACHAT_API_KEY",
        "GIGACHAT_SCOPE",
        "GIGACHAT_API_URL",
        "GIGACHAT_AUTH_URL",
    ]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'установлена' if value else 'пустая'}")
        else:
            print(f"  ❌ {var}: не установлена")
            all_set = False

    return all_set


def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    print("\n📦 Проверка зависимостей:")

    dependencies = [("gigachat", "gigachat"), ("requests", "requests"), ("python-dotenv", "dotenv")]

    all_installed = True
    for friendly_name, module_name in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {friendly_name}: установлена")
        except ImportError:
            print(f"  ❌ {friendly_name}: не установлена")
            all_installed = False

    return all_installed


if __name__ == "__main__":
    print("🤖 Cognitive Agent - Проверка токена GigaChat")
    print("=" * 60)

    # Проверяем зависимости
    deps_ok = check_dependencies()

    # Проверяем переменные окружения
    vars_ok = check_environment_vars()

    print("\n" + "=" * 60)

    # Выполняем проверку токена
    token_ok = check_gigachat_token()

    print("\n" + "=" * 60)
    print("📊 Результат:")

    if token_ok:
        print("🎉 GigaChat настроен правильно!")
        print("✅ Токен успешно получается, можно использовать AI-провайдера")
    else:
        print("⚠️  Требуется настройка GigaChat:")
        if not deps_ok:
            print("   - Установите недостающие зависимости")
        if not vars_ok:
            print("   - Проверьте переменные окружения в .env файле")
        if not token_ok:
            print("   - Проверьте учетные данные GigaChat")

    print("\n📝 Для настройки GigaChat:")
    print("   1. Убедитесь, что в .env файле указаны:")
    print("      GIGACHAT_CLIENT_ID=ваш_client_id")
    print("      GIGACHAT_CLIENT_SECRET=ваш_client_secret")
    print("   2. Или используйте GIGACHAT_API_KEY=ваш_api_ключ")
    print("   3. Перезапустите терминал или выполните: source .venv/Scripts/activate")
