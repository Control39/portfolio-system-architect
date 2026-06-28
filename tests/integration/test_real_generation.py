#!/usr/bin/env python3
"""Реальная генерация тестов с использованием GigaChat API"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Загрузка переменных окружения
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("🚀 Генерация тестов с GigaChat API")
print("=" * 80)

# Проверка переменных окружения
print("\n✅ Проверка переменных окружения:")
print(f"   GIGACHAT_API_KEY: {os.getenv('GIGACHAT_API_KEY', '')[:20]}...")
print(f"   GIGACHAT_CLIENT_ID: {os.getenv('GIGACHAT_CLIENT_ID', '')[:20]}...")
print(f"   PYTHONPATH: {os.getenv('PYTHONPATH', '')}")


async def test_llm_connection():
    """Проверка подключения к GigaChat"""
    print("\n🔒 Проверка подключения к GigaChat...")

    try:
        from agents.cognitive_agent.integrations.llm_client import create_llm_client

        llm_client = create_llm_client()

        if llm_client:
            print("   ✅ LLM client создан успешно")
            provider = getattr(llm_client, "provider_name", type(llm_client).__name__)
            print(f"   Provider: {provider}")

            # Попытка короткого запроса
            test_prompt = "Привет"
            print(f"   Тестовый запрос: '{test_prompt}'...")

            result = await llm_client.generate(prompt=test_prompt, timeout=30)

            if result:
                print(f"   ✅ GigaChat ответил успешно!")
                print(f"   Ответ: {result[:100]}...")
                return True
            else:
                print("   ⚠️ Нет ответа от GigaChat")
                return False
        else:
            print("   ✖️ LLM client не создан")
            return False

    except Exception as e:
        print(f"   ⚠️ Ошибка подключения: {e}")
        return False


async def test_template_loading():
    """Проверка загрузки шаблонов"""
    print("\n📚 Проверка загрузки шаблонов...")

    try:
        from agents.cognitive_agent.src.prompt_engine import PromptEngine
        from pathlib import Path

        prompts_dir = Path("agents/cognitive_agent/prompts")
        root_prompts_dir = Path("prompts")

        engine = PromptEngine(
            prompts_dir=prompts_dir,
            root_prompts_dir=root_prompts_dir,
        )

        print(f"   ✅ PromptEngine инициализирован")
        print(f"   Рамок загружено: {len(engine.templates)}")

        # Проверка загрузки конкретного шаблона
        template = engine.load_template("python/base/unit")
        print(f"   ✅ Шаблон 'python/base/unit' загружен")
        print(f"   Источник: {engine.get_template_source('python/base/unit')}")
        print(f"   Длина: {len(template.content)} символов")

        return True

    except Exception as e:
        print(f"   ✖️ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_code_analysis():
    """Проверка анализа кода"""
    print("\n🔍 Проверка анализа кода...")

    try:
        from agents.cognitive_agent.src.business_logic_analyzer import BusinessLogicAnalyzer

        # Пример кода
        test_code = '''
def add(a: int, b: int) -> int:
    """Сложение двух чисел"""
    if a < 0 or b < 0:
        raise ValueError("Числа должны быть положительными")
    return a + b


def divide(a: int, b: int) -> float:
    """Деление чисел"""
    if b == 0:
        raise ZeroDivisionError("Деление на ноль")
    return a / b
'''

        analyzer = BusinessLogicAnalyzer(test_code)
        result = analyzer.analyze()

        print(f"   ✅ Анализ кода успешен")
        print(f"   Функций: {len(result.get('functions', []))}")
        print(f"   Классов: {len(result.get('classes', []))}")

        if result.get("logic_items"):
            print(f"   Элементов логики:")
            for item in result["logic_items"][:2]:
                print(f"      - {item.get('name')} ({item.get('type')})")

        return True

    except Exception as e:
        print(f"   ✖️ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Основная функция"""

    # Тест 1: Подключение к GigaChat
    chat_ok = await test_llm_connection()

    # Тест 2: Загрузка шаблонов
    templates_ok = await test_template_loading()

    # Тест 3: Анализ кода
    analysis_ok = await test_code_analysis()

    # Результаты
    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 80)

    tests = [
        ("Подключение к GigaChat", chat_ok),
        ("Загрузка шаблонов", templates_ok),
        ("Анализ кода", analysis_ok),
    ]

    all_ok = True
    for name, ok in tests:
        status = "✅" if ok else "❌"
        print(f"{status} {name}")
        if not ok:
            all_ok = False

    print("=" * 80)

    if all_ok:
        print("\n🎉 Все тесты пройдены! Можно приступать к генерации тестов.")
        print("\n💡 Следующие шаги:")
        print("   1. Запустить полную генерацию: python run_test_generation.py")
        print("   2. Или через Autonomous Agent: python run_autonomous_test_gen.py")
    else:
        print("\n⚠️ Некоторые тесты не пройдены. Проверьте конфигурацию.")

    return all_ok


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
