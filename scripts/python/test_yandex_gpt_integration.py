#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции Yandex GPT с проектом portfolio-system-architect.

Этот скрипт проверяет:
1. Наличие и корректность переменных окружения
2. Подключение к Yandex GPT API
3. Работу Python модуля yandex_gpt.py
4. Интеграцию с SourceCraft AI skill
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any

# Добавляем путь к проекту для импорта модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment_variables() -> Dict[str, bool]:
    """Проверка наличия необходимых переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    required_vars = [
        "YANDEX_GPT_API_KEY",
        "YANDEX_GPT_BASE_URL", 
        "YANDEX_GPT_MODEL"
    ]
    
    results = {}
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Маскируем API ключ для безопасности
            if "API_KEY" in var:
                masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
            results[var] = True
        else:
            print(f"  ❌ {var}: не установлена")
            results[var] = False
    
    # Проверка дополнительных переменных
    optional_vars = ["OPENAI_API_KEY", "OPENAI_API_BASE"]
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  📝 {var}: установлена (опционально)")
        else:
            print(f"  ⚠️  {var}: не установлена (можно использовать YANDEX_ переменные)")
    
    return results

def check_python_module() -> bool:
    """Проверка возможности импорта Python модуля"""
    print("\n🔍 Проверка Python модуля yandex_gpt.py...")
    
    try:
        from src.shared.llm.yandex_gpt import (
            YandexGPTConfig,
            YandexGPTClient,
            create_yandex_gpt_client,
            generate_with_yandex_gpt
        )
        
        print("  ✅ Модуль yandex_gpt.py успешно импортирован")
        print(f"  📦 Доступные классы: YandexGPTConfig, YandexGPTClient, create_yandex_gpt_client, generate_with_yandex_gpt")
        
        # Проверка создания конфигурации
        config = YandexGPTConfig()
        print(f"  ⚙️  Конфигурация по умолчанию:")
        print(f"    - model: {config.model}")
        print(f"    - base_url: {config.base_url}")
        print(f"    - temperature: {config.temperature}")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Ошибка импорта модуля: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка при проверке модуля: {e}")
        return False

def check_sourcecraft_config() -> bool:
    """Проверка конфигурации SourceCraft AI skill"""
    print("\n🔍 Проверка конфигурации SourceCraft AI skill...")
    
    skill_path = project_root / ".sourcecraft" / "skills" / "repo-audit-assistant.yml"
    
    if not skill_path.exists():
        print(f"  ❌ Файл конфигурации не найден: {skill_path}")
        return False
    
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие ключевых элементов
        checks = [
            ("name: repo-audit-assistant", "Название навыка"),
            ("llm_providers:", "Конфигурация LLM провайдеров"),
            ("yandex_gpt", "Упоминание Yandex GPT"),
            ("YANDEX_GPT_API_KEY", "Переменная окружения API ключа"),
        ]
        
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✅ {description}: найдено")
            else:
                print(f"  ⚠️  {description}: не найдено")
                all_passed = False
        
        print(f"  📄 Файл конфигурации: {skill_path}")
        print(f"  📏 Размер файла: {len(content)} байт")
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Ошибка при чтении конфигурации: {e}")
        return False

async def test_yandex_gpt_connection() -> bool:
    """Тестирование подключения к Yandex GPT API"""
    print("\n🔍 Тестирование подключения к Yandex GPT API...")
    
    try:
        from src.shared.llm.yandex_gpt import create_yandex_gpt_client
        
        # Создаем клиент
        client = create_yandex_gpt_client()
        
        # Проверяем конфигурацию клиента
        config = client.get_config()
        print(f"  ⚙️  Конфигурация клиента:")
        print(f"    - API URL: {config.get('base_url')}")
        print(f"    - Модель: {config.get('model')}")
        print(f"    - API ключ: {'установлен' if config.get('api_key') else 'отсутствует'}")
        
        # Проверяем наличие API ключа
        if not config.get('api_key') or config.get('api_key') == 'your_yandex_gpt_api_key_here':
            print("  ⚠️  API ключ не установлен или имеет значение по умолчанию")
            print("     Установите YANDEX_GPT_API_KEY в .env файле")
            return False
        
        # Пробуем выполнить тестовый запрос (если API ключ валиден)
        print("  🚀 Выполнение тестового запроса...")
        
        try:
            # Используем короткий промпт для минимизации затрат
            test_prompt = "Привет! Ответь коротко: 'Тест подключения успешен'"
            
            # Проверяем, нужно ли выполнять реальный запрос к API
            test_real_api = os.environ.get("YANDEX_GPT_TEST_REAL_API", "").lower() == "true"
            
            if test_real_api:
                print("  🔧 Режим реального API: выполняется запрос к Yandex GPT...")
                response = await client.generate(
                    prompt=test_prompt,
                    system_message="Ты тестовый ассистент. Отвечай кратко."
                )
                print(f"  ✅ Ответ от Yandex GPT: {response[:100]}...")
                print("  ✅ Реальный запрос к API выполнен успешно")
                return True
            else:
                # Режим mock для экономии токенов
                print("  ⚠️  Режим mock: реальный запрос к API отключен для экономии токенов")
                print("     Для реального теста установите переменную окружения:")
                print("     export YANDEX_GPT_TEST_REAL_API=true")
                
                # Проверяем, что клиент создан корректно
                if client.client:
                    print("  ✅ Клиент Yandex GPT инициализирован корректно")
                    return True
                else:
                    print("  ❌ Клиент Yandex GPT не инициализирован")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Ошибка при тестовом запросе: {e}")
            print(f"     Проверьте:")
            print(f"     1. Корректность API ключа")
            print(f"     2. Доступность {config.get('base_url')}")
            print(f"     3. Наличие квот в Yandex Cloud")
            return False
            
    except Exception as e:
        print(f"  ❌ Ошибка при создании клиента: {e}")
        return False

def generate_test_report(results: Dict[str, Any]) -> None:
    """Генерация отчета о тестировании"""
    print("\n" + "="*60)
    print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ ИНТЕГРАЦИИ YANDEX GPT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"\n📈 Статистика:")
    print(f"  Всего тестов: {total_tests}")
    print(f"  Пройдено: {passed_tests}")
    print(f"  Не пройдено: {total_tests - passed_tests}")
    
    print(f"\n🔍 Результаты по тестам:")
    for test_name, passed in results.items():
        status = "✅ ПРОЙДЕН" if passed else "❌ НЕ ПРОЙДЕН"
        print(f"  {status}: {test_name}")
    
    print(f"\n💡 Рекомендации:")
    
    if not all(results.values()):
        print("  1. Проверьте переменные окружения в .env файле")
        print("  2. Убедитесь, что API ключ Yandex GPT корректен")
        print("  3. Проверьте доступность Yandex Cloud AI API")
        print("  4. Убедитесь, что все зависимости установлены")
    else:
        print("  1. Все тесты пройдены успешно!")
        print("  2. Интеграция Yandex GPT готова к использованию")
        print("  3. Можно приступать к использованию AI skill в SourceCraft")
    
    print(f"\n🚀 Следующие шаги:")
    print("  1. Заполните реальный API ключ в .env файле")
    print("  2. Протестируйте работу AI skill в SourceCraft")
    print("  3. Интегрируйте Yandex GPT в свои приложения")
    print("  4. Настройте мониторинг использования API")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования интеграции Yandex GPT")
    print("="*60)
    
    results = {}
    
    # Проверка переменных окружения
    env_results = check_environment_variables()
    results["Переменные окружения"] = all(env_results.values())
    
    # Проверка Python модуля
    results["Python модуль"] = check_python_module()
    
    # Проверка конфигурации SourceCraft
    results["Конфигурация SourceCraft"] = check_sourcecraft_config()
    
    # Тестирование подключения к Yandex GPT
    results["Подключение к Yandex GPT API"] = await test_yandex_gpt_connection()
    
    # Генерация отчета
    generate_test_report(results)
    
    # Возвращаем код выхода
    if all(results.values()):
        print("\n🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("\n⚠️  Некоторые тесты не пройдены. Проверьте рекомендации выше.")
        return 1

if __name__ == "__main__":
    # Загружаем переменные окружения из .env файла
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"📁 Загружены переменные окружения из: {env_path}")
    else:
        print(f"⚠️  Файл .env не найден. Использую системные переменные окружения.")
    
    # Запускаем тестирование
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

