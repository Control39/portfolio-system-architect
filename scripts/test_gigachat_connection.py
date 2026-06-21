#!/usr/bin/env python3
"""
Скрипт для проверки подключения к GigaChat API
Проверяет настройки, токен и возможность отправки тестового запроса
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def test_gigachat_connection():
    """Тестирует подключение к GigaChat API"""
    print("🔍 Проверка подключения к GigaChat API...")
    print("=" * 60)

    # Проверяем наличие переменных окружения
    print("\n📋 Проверка переменных окружения:")

    required_vars = [
        "GIGACHAT_API_KEY",
        "GIGACHAT_CLIENT_ID",
        "GIGACHAT_CLIENT_SECRET",
        "GIGACHAT_SCOPE",
        "GIGACHAT_API_URL",
        "GIGACHAT_AUTH_URL",
    ]

    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Маскируем чувствительные данные
            if "KEY" in var or "SECRET" in var or "ID" in var:
                display_value = value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: не установлена")

    # Проверяем конфигурацию через ConfigManager
    print("\n⚙️ Проверка ConfigManager:")
    try:
        from apps.ai_config_manager.src.ai_config_manager import ConfigManager

        # Проверяем, что файл конфигурации существует
        config_path = repo_root / "config" / "ai-config.yaml"

        if config_path.exists():
            print(f"  ✅ Файл конфигурации найден: {config_path}")

            # Создаем ConfigManager
            config_manager = ConfigManager(str(config_path))
            print("  ✅ ConfigManager инициализирован")

            # Пробуем получить токен GigaChat
            token = config_manager.get_gigachat_token()
            if token:
                print("  ✅ Токен GigaChat успешно получен")
                print(f"  📜 Токен: {token[:20]}...{token[-10:] if len(token) > 30 else token}")
            else:
                print("  ❌ Не удалось получить токен GigaChat")
                print("     Проверьте настройки в .env файле")
        else:
            print(f"  ❌ Файл конфигурации не найден: {config_path}")
            print("     Создайте файл по образцу: config/ai-config.yaml.example")

    except ImportError as e:
        print(f"  ❌ Ошибка импорта ConfigManager: {e}")
    except Exception as e:
        print(f"  ❌ Ошибка при работе с ConfigManager: {e}")

    # Проверяем доступность библиотек
    print("\n📦 Проверка установленных библиотек:")

    libraries = [
        ("gigachat", "gigachat"),
        ("langchain_gigachat", "langchain_gigachat"),
        ("langchain_community", "langchain_community.llms"),
    ]

    for lib_name, import_path in libraries:
        try:
            if "." in import_path:
                parts = import_path.split(".")
                module = __import__(parts[0])
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(import_path)
            print(f"  ✅ {lib_name}: установлен")
        except ImportError:
            print(f"  ❌ {lib_name}: не установлен")

    # Тестируем AI Provider Manager
    print("\n🤖 Проверка AI Provider Manager:")
    try:
        from apps.ai_provider_manager.src.ai_provider_manager import AIProviderManager

        provider_manager = AIProviderManager()
        status = provider_manager.get_status()

        print("  ✅ AI Provider Manager инициализирован")
        for provider, info in status.items():
            print(f"    {provider}: {info['status']}")

        # Пробуем отправить тестовый запрос
        print("\n🧪 Тестовый запрос к AI:")
        test_messages = [{"role": "user", "content": "Привет, это тестовое сообщение. Ответь кратко."}]
        response = provider_manager.chat(test_messages, temperature=0.7)

        if response:
            print(f"  ✅ Ответ получен: {response[:100]}...")
        else:
            print("  ❌ Не удалось получить ответ от AI")

    except ImportError as e:
        print(f"  ❌ Ошибка импорта AI Provider Manager: {e}")
    except Exception as e:
        print(f"  ❌ Ошибка при работе с AI Provider Manager: {e}")

    print("\n" + "=" * 60)
    print("📋 Рекомендации:")
    print("  1. Убедитесь, что все переменные окружения установлены в .env")
    print("  2. Проверьте, что учетные данные GigaChat действительны")
    print("  3. Установите недостающие библиотеки при необходимости")
    print("  4. Перезапустите виртуальное окружение после изменений")


def setup_gigachat_config():
    """Помогает настроить подключение к GigaChat"""
    print("\n🔧 Настройка подключения к GigaChat...")

    # Проверяем наличие .env файла
    env_path = repo_root / ".env"

    if not env_path.exists():
        print(f"  ⚠️ Файл {env_path} не найден")
        create_example = input("  Создать файл .env с примером настроек? (y/n): ")

        if create_example.lower() == "y":
            create_env_example(env_path)
    else:
        print(f"  ✅ Файл {env_path} найден")

        # Проверяем, заполнены ли основные поля
        with open(env_path, encoding="utf-8") as f:
            content = f.read()

        required_fields = ["GIGACHAT_CLIENT_ID", "GIGACHAT_CLIENT_SECRET"]
        missing_fields = []

        for field in required_fields:
            if field not in content:
                missing_fields.append(field)

        if missing_fields:
            print(f"  ⚠️ В файле .env отсутствуют поля: {', '.join(missing_fields)}")
            print("     Добавьте их вручную или используйте команду:")
            print(f"     echo 'GIGACHAT_CLIENT_ID=ваш_client_id' >> {env_path}")
            print(f"     echo 'GIGACHAT_CLIENT_SECRET=ваш_client_secret' >> {env_path}")


def create_env_example(env_path):
    """Создает пример файла .env"""
    example_content = """# GigaChat API Configuration
GIGACHAT_API_KEY=ваш_api_ключ_здесь
GIGACHAT_CLIENT_ID=ваш_client_id
GIGACHAT_CLIENT_SECRET=ваш_client_secret
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_API_URL=https://gigachat.devices.sberbank.ru/api/v1
GIGACHAT_AUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth

# Other settings
OLLAMA_URL=http://localhost:11434
"""

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(example_content)

    print(f"  ✅ Создан файл {env_path} с примером настроек")
    print("     ЗАПОЛНИТЕ РЕАЛЬНЫМИ ДАННЫМИ!")


if __name__ == "__main__":
    print("🤖 Cognitive Agent - Проверка подключения к GigaChat")

    # Загружаем переменные окружения
    env_path = repo_root / ".env"
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv(env_path)

    test_gigachat_connection()
    setup_gigachat_config()
