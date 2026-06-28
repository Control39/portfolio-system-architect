#!/usr/bin/env python3
"""Запуск генерации тестов для src/ через TestGenerator"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к агенту
sys.path.insert(0, str(Path(__file__).parent))

from agents.cognitive_agent.src.test_generator import TestGenerator
from agents.cognitive_agent.src.prompt_engine import PromptEngine


async def main():
    """Запустить генерацию тестов для src/"""

    print("=" * 80)
    print("🤖 Запуск TestGenerator для src/")
    print("=" * 80)

    # Инициализация TestGenerator с поддержкой корневых шаблонов
    src_path = Path("C:/repo/src")
    prompts_dir = Path("agents/cognitive_agent/prompts")
    root_prompts_dir = Path("prompts")

    generator = TestGenerator(
        project_path=str(src_path),
        prompts_dir=prompts_dir,
        root_prompts_dir=root_prompts_dir,
    )

    print(f"\n✅ Инициализирован TestGenerator")
    print(f"   Путь: {src_path}")
    print(f"   Шаблонов загружено: {len(generator.prompt_engine.templates)}")

    # Получить список Python файлов без тестов
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

    print(f"\n📋 Найдено Python файлов без тестов: {len(py_files)}")
    print("   Файлы:")
    for f in py_files[:5]:
        print(f"      • {f.relative_to(src_path)}")
    if len(py_files) > 5:
        print(f"      ... и ещё {len(py_files) - 5} файлов")

    # 🚀 ГЕНЕРАЦИЯ ТЕСТОВ ДЛЯ ПЕРВЫХ 3 ФАЙЛОВ (для демонстрации)
    print("\n" + "=" * 80)
    print("🧪 ГЕНЕРАЦИЯ ТЕСТОВ (первые 3 файла для демонстрации)")
    print("=" * 80)

    results = []

    for file_path in py_files[:3]:
        print(f"\n📝 Обработка: {file_path.relative_to(src_path)}")

        try:
            # Анализ бизнес-логики
            from agents.cognitive_agent.src.business_logic_analyzer import BusinessLogicAnalyzer
            import json

            code = file_path.read_text(encoding="utf-8")
            analyzer = BusinessLogicAnalyzer(code)
            logic_result = analyzer.analyze()

            print(f"   ✓ Анализ бизнес-логики:")
            print(f"      • Функций: {len(logic_result.get('functions', []))}")
            print(f"      • Классов: {len(logic_result.get('classes', []))}")
            print(f"      • Моделей: {len(logic_result.get('models', []))}")

            if logic_result.get("logic_items"):
                print(f"      • Элементов логики:")
                for item in logic_result["logic_items"][:2]:
                    print(f"         - {item['type']}: {item['name']} (lines {item['line_range']})")
                if len(logic_result["logic_items"]) > 2:
                    print(f"         ... и ещё {len(logic_result['logic_items']) - 2} элементов")

            # Генерация (пока без LLM - демонстрация анализа)
            framework = generator._detect_framework(file_path)
            file_type = generator._detect_file_type(file_path, framework)
            template = generator._get_template_path(framework, file_type)

            print(f"   ✓ Подготовка генерации:")
            print(f"      • Фреймворк: {framework}")
            print(f"      • Тип файла: {file_type}")
            print(f"      • Шаблон: {template}")

            # Показать, какой контекст будет отправлен в LLM
            context = {
                "repo_path": str(src_path),
                "service_name": str(file_path.parent.relative_to(src_path)),
                "python_version": "3.12",
                "framework": framework,
                "current_coverage": "0",
                "coverage_target": "85",
                "file_path": str(file_path),
                "file_type": file_type,
                "code": code[:200] + "...",
            }

            if logic_result:
                context["business_logic"] = json.dumps(
                    {k: v for k, v in logic_result.items() if k in ["functions", "classes", "models"]},
                    ensure_ascii=False,
                    indent=2,
                )

            # Вывести промпт (первые 500 символов)
            prompt_engine = PromptEngine(prompts_dir=prompts_dir)
            rendered = prompt_engine.render(template, context)
            print(f"\n   📋 Пример промпта для LLM:")
            print(f"      {rendered[:500]}...")

            results.append(
                {
                    "file": str(file_path.relative_to(src_path)),
                    "success": True,
                    "framework": framework,
                    "file_type": file_type,
                    "template": template,
                    "logic_items": len(logic_result.get("logic_items", [])),
                }
            )

        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
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

    success_count = sum(1 for r in results if r["success"])
    print(f"\n✅ Успешно обработано: {success_count}/{len(results)}")

    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"   {status} {r['file']}")
        if r["success"]:
            print(f"      Framework: {r['framework']}, Type: {r['file_type']}")
            print(f"      Template: {r['template']}")
            print(f"      Logic Items: {r['logic_items']}")

    print("\n" + "=" * 80)
    print("🚀 ДЛЯ ПОЛНОЙ ГЕНЕРАЦИИ ТЕСТОВ НУЖЕН LLM КЛИЕНТ")
    print("=" * 80)
    print("\n💡 Чтобы запустить полную генерацию:")
    print("   1. Инициализировать ai_provider в AutonomousAgent")
    print("   2. Передать llm_client в generate_test_for_file()")
    print("   3. Вызвать generate_tests_for_directory()")
    print("\n💡 Пример:")
    print("   from agents.cognitive_agent.src.test_generator import TestGenerator")
    print("   from agents.cognitive_agent.integrations import AIProviderIntegration")
    print("")
    print("   generator = TestGenerator(project_path='C:/repo/src')")
    print("   ai_provider = AIProviderIntegration()")
    print("   results = await generator.generate_tests_for_directory(")
    print("       directory='C:/repo/src',")
    print("       llm_client=ai_provider.llm_client,")
    print("   )")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
