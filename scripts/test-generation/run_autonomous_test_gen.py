#!/usr/bin/env python3
"""Запуск AutonomousAgent с генерацией тестов для src/"""

import asyncio
import os
import sys
from pathlib import Path

# Установить переменные окружения ДО импортов
os.environ["GIGACHAT_VERIFY_SSL"] = "false"

# Добавляем путь к агенту
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent


async def main():
    """Запустить AutonomousAgent и сгенерировать тесты"""

    print("=" * 80)
    print("🤖 Запуск AutonomousAgent с генерацией тестов")
    print("=" * 80)

    # Инициализация агента
    print("\n🚀 Инициализация AutonomousAgent...")
    agent = AutonomousCognitiveAgent(project_path="C:/repo")

    print(f"✅ Агент инициализирован")
    print(f"   Agent ID: {agent.agent_id}")
    print(f"   Project: {agent.project_path}")
    print(f"   Prompt Engine: {len(agent.prompt_engine.templates)} шаблонов")
    print(f"   Test Generator: {type(agent.test_generator).__name__}")

    # Получить TestGenerator
    generator = agent.test_generator

    # Получить список файлов для генерации
    src_path = Path("C:/repo/src")
    py_files = []
    for pattern in ["*.py", "**/*.py"]:
        for file_path in src_path.glob(pattern):
            if not file_path.is_file():
                continue
            if "test" in file_path.name.lower():
                continue
            if "__pycache__" in str(file_path):
                continue
            py_files.append(file_path)

    print(f"\n📋 Найдено Python файлов без тестов в src/: {len(py_files)}")

    # Получить LLM client
    print("\n🔐 Проверка LLM клиента...")
    # Проверить через test_generator
    if hasattr(generator, "llm_client") and generator.llm_client:
        print("   ✓ LLM client доступен через test_generator")
        llm_client = generator.llm_client
    elif generator.prompt_engine.llm_client:
        print("   ✓ LLM client доступен через prompt_engine")
        llm_client = generator.prompt_engine.llm_client
    elif agent.ai_provider and hasattr(agent.ai_provider, "llm_client"):
        print("   ✓ LLM client доступен через ai_provider")
        llm_client = agent.ai_provider.llm_client
    else:
        print("   ⚠️ LLM client не найден - покажу только анализ")
        llm_client = None

    # Генерация для первых 5 файлов
    print("\n" + "=" * 80)
    print("🧪 ГЕНЕРАЦИЯ ТЕСТОВ (первые 5 файлов)")
    print("=" * 80)

    results = []

    for i, file_path in enumerate(py_files[:5], 1):
        print(f"\n📝 [{i}/5] Обработка: {file_path.relative_to(src_path)}")

        try:
            # Анализ бизнес-логики
            if llm_client is None:
                # Только анализ без LLM
                from agents.cognitive_agent.src.business_logic_analyzer import BusinessLogicAnalyzer

                code = file_path.read_text(encoding="utf-8")
                analyzer = BusinessLogicAnalyzer(code)
                logic_result = analyzer.analyze()

                framework = generator._detect_framework(file_path)
                file_type = generator._detect_file_type(file_path, framework)
                template = generator._get_template_path(framework, file_type)

                print(f"   ✓ Анализ (без LLM):")
                print(f"      • Функций: {len(logic_result.get('functions', []))}")
                print(f"      • Классов: {len(logic_result.get('classes', []))}")
                print(f"      • Фреймворк: {framework}, Тип: {file_type}")
                print(f"      • Шаблон: {template}")

                results.append(
                    {
                        "file": str(file_path.relative_to(src_path)),
                        "success": True,
                        "analysis_only": True,
                        "logic_items": len(logic_result.get("logic_items", [])),
                    }
                )

            else:
                # Полная генерация с LLM
                print(f"   🚀 Генерация тестов через LLM...")
                result = await generator.generate_test_for_file(
                    file_path=file_path,
                    llm_client=llm_client,
                    target_coverage=85,
                )

                if result["success"]:
                    print(f"   ✅ Генерация успешна!")
                    print(f"      • Template: {result['template_used']}")
                    print(f"      • Prompt length: {result['prompt_length']}")
                    print(f"      • Response length: {result['response_length']}")

                    # Сохранить тесты
                    output_file = file_path.parent / f"test_{file_path.stem}.py"
                    generator.apply_generated_tests(
                        test_code=result["output"],
                        output_file=output_file,
                        mode="overwrite",
                    )
                    print(f"      • Сохранено: {output_file}")
                else:
                    print(f"   ✗ Генерация не удалась")
                    print(f"      • Error: {result.get('error', 'Unknown')}")

                results.append(result)

        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            import traceback

            traceback.print_exc()
            results.append(
                {
                    "file": str(file_path.relative_to(src_path)),
                    "success": False,
                    "error": str(e),
                }
            )

    # Итоговый отчёт
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 80)

    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
    print(f"\n✅ Успешно обработано: {success_count}/{len(results)}")

    for r in results:
        if isinstance(r, dict):
            status = "✓" if r.get("success", False) else "✗"
            filename = r.get("file", r.get("file_path", "unknown"))
            print(f"   {status} {filename}")
            if r.get("analysis_only"):
                print(f"      (Анализ без LLM)")
            if r.get("error"):
                print(f"      (Error: {r['error'][:100]}...)")
        else:
            print(f"   ✗ Unknown result: {r}")

    print("\n" + "=" * 80)
    print("🎉 ЗАПУСК ЗАВЕРШЕН")
    print("=" * 80)
    print("\n💡 Для полной генерации всех файлов:")
    print("   results = await generator.generate_tests_for_directory(")
    print("       directory='C:/repo/src',")
    print("       llm_client=llm_client,")
    print("   )")
    print("\n💡 Для мониторинга изменений:")
    print("   from agents.cognitive_agent.src.test_generator_watcher import TestGeneratorWatcher")
    print("   watcher = TestGeneratorWatcher(")
    print("       project_path='C:/repo/src',")
    print("       prompts_dir=Path('agents/cognitive_agent/prompts'),")
    print("       llm_client=llm_client,")
    print("   )")
    print("   await watcher.start()")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
