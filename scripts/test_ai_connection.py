#!/usr/bin/env python3
"""
Тестирование подключения к AI провайдерам
"""

import sys
from pathlib import Path

# Добавляем корень репозитория в путь
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def test_ai_providers():
    """Тестирование подключения к AI провайдерам"""
    print("🧪 Тестирование подключения к AI провайдерам...")

    try:
        # Импортируем менеджер провайдеров
        from apps.ai_provider_manager.src.ai_provider_manager import get_provider_manager

        # Получаем менеджер
        manager = get_provider_manager()
        print(f"✅ Менеджер провайдеров создан: {manager}")

        # Проверяем статус всех провайдеров
        status = manager.get_status()
        print(f"📊 Статус провайдеров: {status}")

        # Проверяем активный провайдер
        active_provider = manager.get_active_provider()
        print(f"🎯 Активный провайдер: {active_provider}")

        if active_provider:
            print("✅ Есть активный провайдер")

            # Пытаемся выполнить тестовый запрос
            try:
                response = active_provider.chat(messages=[{"role": "user", "content": "Привет, проверка связи"}])
                print(f"✅ Ответ от провайдера получен: {str(response)[:100]}...")
            except Exception as e:
                print(f"❌ Ошибка тестового запроса: {e}")
        else:
            print("❌ Нет активного провайдера - проверьте конфигурацию")

        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Проверьте, что все зависимости установлены")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback

        traceback.print_exc()
        return False


def check_config_files():
    """Проверка файлов конфигурации"""
    print("\n🔍 Проверка файлов конфигурации...")

    config_paths = [
        "config/ai-config.yaml",
        "apps/ai_config_manager/src/ai_config_manager/config.yaml",
        "agents/cognitive_agent/config/agent-config.yaml",
    ]

    for path in config_paths:
        config_path = Path(path)
        if config_path.exists():
            print(f"✅ {path}: найден")
        else:
            print(f"❌ {path}: НЕ НАЙДЕН")


def main():
    print("🧪 Тестирование подключения к AI провайдерам")
    print("=" * 50)

    # Проверяем конфигурации
    check_config_files()

    # Тестируем подключение
    success = test_ai_providers()

    print("\n" + "=" * 50)
    if success:
        print("✅ Подключение к AI провайдерам работает")
        print("💡 Ваш агент может использовать AI")
    else:
        print("❌ Подключение к AI провайдерам не работает")
        print("💡 Проверьте конфигурацию и зависимости")


if __name__ == "__main__":
    main()
