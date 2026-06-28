#!/usr/bin/env python3
"""Извлечение тестов из сгенерированного ответа LLM"""

import re
from pathlib import Path


def extract_code_blocks(text: str) -> list[str]:
    """
    Извлечь все блоки кода из текста (markdown или plain)

    Returns:
        Список блоков кода (последний - это сгенерированные тесты)
    """
    blocks = []

    # Markdown блоки
    markdown_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    blocks.extend(re.findall(markdown_pattern, text))

    # Plain текст между маркерами
    # Ищем код между "Код для анализа:" и "Формат ответа:"
    code_marker = r"Код для анализа:\s*([\s\S]*?)(?:Формат ответа:|$)"
    code_match = re.search(code_marker, text)
    if code_match:
        blocks.append(code_match.group(1).strip())

    # Ищем код после "Формат ответа:"
    format_marker = r"Формат ответа:.*?([\s\S]*)$"
    format_match = re.search(format_marker, text, re.DOTALL)
    if format_match:
        blocks.append(format_match.group(1).strip())

    return blocks


def extract_tests_from_file(file_path: Path) -> str | None:
    """
    Извлечь тесты из файла

    Args:
        file_path: Путь к файлу

    Returns:
        Извлеченный код или None
    """
    content = file_path.read_text(encoding="utf-8")

    # Если файл уже содержит тесты, не трогаем
    if content.strip().startswith("def test_") or content.strip().startswith("import pytest"):
        print(f"- Already has tests: {file_path}")
        return None

    # Извлечь все блоки кода
    blocks = extract_code_blocks(content)

    if not blocks:
        print(f"- No code blocks found: {file_path}")
        return None

    # Вернуть последний блок (он должен содержать тесты)
    code = blocks[-1].strip()

    # Удалить комментарии в начале
    lines = code.split("\n")
    while lines and (
        lines[0].strip().startswith("#") or lines[0].strip().startswith('"') or lines[0].strip().startswith("'")
    ):
        lines.pop(0)

    code = "\n".join(lines).strip()

    # Проверить, что это действительно тесты
    if "def test_" in code:
        print(f"✓ Extracted tests from: {file_path}")
        return code
    else:
        print(f"- Last block is not tests: {file_path}")
        return None


def fix_all_test_files():
    """Исправить все тестовые файлы"""
    src_path = Path("C:/repo/src")

    fixed = 0

    # Поиск всех файлов test_*.py
    for test_file in list(src_path.glob("test_*.py")) + list(src_path.rglob("test_*.py")):
        if test_file.is_file():
            extracted = extract_tests_from_file(test_file)
            if extracted:
                test_file.write_text(extracted, encoding="utf-8")
                fixed += 1

    print(f"\n✅ Fixed {fixed} files")


if __name__ == "__main__":
    fix_all_test_files()
