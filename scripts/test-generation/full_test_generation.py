#!/usr/bin/env python3
"""Полная генерация тестов для всех Python файлов в src/"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "C:/repo")

from agents.cognitive_agent.autonomous_agent import AutonomousCognitiveAgent


async def full_generation():
    print("=" * 80)
    print("🤖 ПОЛНАЯ ГЕНЕРАЦИЯ ТЕСТОВ ДЛЯ ВСЕХ ФАЙЛОВ В src/")
    print("=" * 80)

    agent = AutonomousCognitiveAgent(project_path="C:/repo")
    generator = agent.test_generator
    llm_client = generator.llm_client

    # Сканировать все файлы в src/
    src_path = Path("C:/repo/src")
    py_files = []
    for pattern in ["*.py", "**/*.py"]:
        for f in src_path.glob(pattern):
            if f.is_file() and "test" not in f.name.lower() and "__pycache__" not in str(f):
                py_files.append(f)

    print(f"\n📋 Найдено {len(py_files)} Python файлов для обработки")

    # Генерация тестов
    results = await generator.generate_tests_for_directory(
        directory="C:/repo/src",
        llm_client=llm_client,
        target_coverage=85,
    )

    # Итоги
    success = sum(1 for r in results if r.get("success"))
    print(f"\n✅ Сгенерировано: {success}/{len(results)}")

    for r in results:
        status = "✓" if r.get("success") else "✗"
        file_path = r.get("file_path", "unknown")
        response_len = r.get("response_length", 0)
        print(f"  {status} {file_path} (response: {response_len} символов)")

    print("\n" + "=" * 80)
    print("🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(full_generation())
