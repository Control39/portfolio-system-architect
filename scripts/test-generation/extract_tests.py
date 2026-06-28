#!/usr/bin/env python3
"""Умное извлечение тестов из сгенерированного кода"""

import re
from pathlib import Path


def extract_tests_from_response(response: str) -> str:
    """
    Извлечь Python код с тестами из ответа LLM

    Паттерны для поиска:
    1. ```python ... ```
    2. Код после "Код для анализа:"
    3. Код после "def test_" (первый тест)

    Args:
        response: Ответ от LLM

    Returns:
        Извлеченный код с тестами
    """
    # Паттерн 1: markdown блоки с кодом
    markdown_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    markdown_matches = re.findall(markdown_pattern, response)

    if markdown_matches:
        # Вернуть последний markdown блок (он содержит сгенерированные тесты)
        return markdown_matches[-1].strip()

    # Паттерн 2: код после "Код для анализа:" или похожих маркеров
    analysis_markers = [
        r"Код для анализа:(.*)",
        r"Here is the test code:(.*)",
        r"```python(.*)",
    ]

    for marker in analysis_markers:
        match = re.search(marker, response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            # Удалить лишние строки в начале
            lines = code.split("\n")
            while lines and lines[0].strip().startswith("#"):
                lines.pop(0)
            return "\n".join(lines).strip()

    # Паттерн 3: искать первый тест и вернуть всё после него
    test_pattern = r"(def test_[a-z_]+.*?)"
    match = re.search(test_pattern, response, re.DOTALL)

    if match:
        # Вернуть всё, что содержит тесты
        start = match.start()
        # Найти последний тест
        all_tests = re.findall(
            r"(def test_[a-z_]+.*?)(?=\n(?:def |class |@pytest|)$|\\Z)", response[start:], re.DOTALL | re.MULTILINE
        )
        if all_tests:
            return "\n".join(all_tests).strip()

    # Если ничего не найдено, вернуть как есть
    return response


def fix_test_file(file_path: Path) -> bool:
    """
    Исправить файл с тестами

    Args:
        file_path: Путь к файлу

    Returns:
        True если файл был исправлен
    """
    content = file_path.read_text(encoding="utf-8")

    # Проверить, содержит ли файл тесты
    if "def test_" in content:
        # Файл уже содержит тесты
        return False

    # Попробовать извлечь тесты
    extracted = extract_tests_from_response(content)

    if "def test_" in extracted:
        # Сохранить извлеченный код
        file_path.write_text(extracted, encoding="utf-8")
        print(f"✓ Fixed: {file_path}")
        return True
    else:
        print(f"✗ Cannot extract tests from: {file_path}")
        return False


if __name__ == "__main__":
    # Обработать все файлы test_*.py в src/
    src_path = Path("C:/repo/src")

    fixed_count = 0
    total_count = 0

    for test_file in src_path.glob("test_*.py"):
        if test_file.is_file():
            total_count += 1
            if fix_test_file(test_file):
                fixed_count += 1

    # Также в поддиректориях
    for test_file in src_path.rglob("test_*.py"):
        if test_file.is_file():
            total_count += 1
            if fix_test_file(test_file):
                fixed_count += 1

    print(f"\n✅ Processed: {total_count} files, {fixed_count} fixed")
