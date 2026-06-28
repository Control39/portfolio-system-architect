#!/usr/bin/env python3
"""Полная генерация тестов для всех Python файлов в src/"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/repo")

from agents.cognitive_agent.src.test_generator import TestGenerator
from agents.cognitive_agent.integrations.llm_client import create_llm_client


async def generate_all_files():
    """Генерация тестов для всех файлов"""
    print("=" * 80)
    print("🤖 ПОЛНАЯ ГЕНЕРАЦИЯ ТЕСТОВ ДЛЯ ВСЕХ ФАЙЛОВ В src/")
    print("=" * 80)

    generator = TestGenerator(
        project_path="C:/repo",
        prompts_dir=Path("agents/cognitive_agent/prompts"),
        root_prompts_dir=Path("prompts"),
        llm_client=create_llm_client(),
    )

    # Сканировать все файлы в src/
    src_path = Path("C:/repo/src")
    py_files = []
    for pattern in ["*.py", "**/*.py"]:
        for f in src_path.glob(pattern):
            if f.is_file() and "test" not in f.name.lower() and "__pycache__" not in str(f):
                py_files.append(f)

    print(f"\n📋 Найдено {len(py_files)} Python файлов для обработки")
    print(f"⏱️  Ожидаемое время: ~{len(py_files) * 15 / 60:.1f} минут (по 15 сек на файл)")

    results = []
    for i, file_path in enumerate(py_files, 1):
        print(f"\n[{i}/{len(py_files)}] Генерация для: {file_path.relative_to(src_path)}")

        try:
            # 2 минуты таймаут на файл
            result = await asyncio.wait_for(
                generator.generate_test_for_file(
                    file_path=str(file_path),
                    llm_client=generator.llm_client,
                    target_coverage=85,
                ),
                timeout=120,
            )

            success = result.get("success", False)
            status = "✅" if success else "❌"
            print(
                f"  {status} {file_path.relative_to(src_path)} (response: {result.get('response_length', 0)} символов)"
            )

            results.append(result)

        except asyncio.TimeoutError:
            print(f"  ⏰ Таймаут! Пропускаем файл: {file_path.relative_to(src_path)}")
            results.append({"success": False, "file_path": str(file_path), "error": "timeout"})
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            results.append({"success": False, "file_path": str(file_path), "error": str(e)})

    # Итоги
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n{'=' * 80}")
    print(f"✅ Успешно: {success_count}/{len(results)}")
    print(f"{'=' * 80}")

    return results


if __name__ == "__main__":
    asyncio.run(generate_all_files())
