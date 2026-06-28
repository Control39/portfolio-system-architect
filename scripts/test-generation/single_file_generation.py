#!/usr/bin/env python3
"""Генерация тестов для одного файла с таймаутом"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/repo")

from agents.cognitive_agent.src.test_generator import TestGenerator
from agents.cognitive_agent.integrations.llm_client import create_llm_client
import signal


async def generate_for_single_file():
    """Генерация для одного файла с таймаутом"""
    print("🚀 Генерация тестов для одного файла...")

    generator = TestGenerator(
        project_path="C:/repo",
        prompts_dir=Path("agents/cognitive_agent/prompts"),
        root_prompts_dir=Path("prompts"),
        llm_client=create_llm_client(),
    )

    # Выбрать первый файл для теста
    src_path = Path("C:/repo/src")
    py_files = []
    for f in src_path.glob("*.py"):
        if f.is_file() and "test" not in f.name.lower() and "__pycache__" not in str(f):
            py_files.append(f)

    if not py_files:
        print("❌ Файлы не найдены")
        return

    target_file = py_files[0]
    print(f"🎯 Целевой файл: {target_file.relative_to(src_path)}")

    # Создать таймаут
    async def generate_with_timeout():
        return await generator.generate_test_for_file(
            file_path=str(target_file),
            llm_client=generator.llm_client,
            target_coverage=85,
        )

    try:
        # 2 минуты таймаут
        result = await asyncio.wait_for(generate_with_timeout(), timeout=120)
        print(f"✅ Результат: {result}")
    except asyncio.TimeoutError:
        print("⏰ Таймаут! Генерация зависла.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(generate_for_single_file())
