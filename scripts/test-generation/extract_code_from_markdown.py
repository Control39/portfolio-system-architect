#!/usr/bin/env python3
"""Извлечение кода из markdown с блоками Python"""

import re
from pathlib import Path


def extract_code_from_markdown(markdown_text: str) -> str:
    """
    Извлечь Python код из markdown текста

    Args:
        markdown_text: Markdown с блоками кода

    Returns:
        Извлеченный Python код
    """
    # Паттерн для поиска кода в markdown блоках
    pattern = r"```(?:python)?\s*([\s\S]*?)```"

    matches = re.findall(pattern, markdown_text)

    if matches:
        # Вернуть **последний** найденный блок кода (он содержит сгенерированные тесты)
        code = matches[-1].strip()
        # Удалить строку с описанием (если есть)
        if code.startswith("# "):
            lines = code.split("\n")
            # Удалить первые строки, которые начинаются с "#"
            while lines and lines[0].startswith("#"):
                lines.pop(0)
            code = "\n".join(lines).strip()
        return code
    else:
        # Если нет markdown блоков, вернуть как есть
        return markdown_text


def process_test_file(file_path: Path) -> None:
    """
    Обработать файл с тестами и извлечь код

    Args:
        file_path: Путь к файлу с тестами
    """
    content = file_path.read_text(encoding="utf-8")

    # Проверить, содержит ли файл markdown блоки
    if "```python" in content or "```" in content:
        print(f"Processing: {file_path}")

        # Извлечь код
        extracted_code = extract_code_from_markdown(content)

        # Сохранить обратно
        file_path.write_text(extracted_code, encoding="utf-8")
        print(f"  ✓ Extracted code from markdown")


if __name__ == "__main__":
    # Обработать все файлы test_*.py в src/
    src_path = Path("C:/repo/src")

    for pattern in ["test_*.py", "test_*.md"]:
        for test_file in src_path.glob(pattern):
            if test_file.is_file():
                process_test_file(test_file)

    # Также обработать в поддиректориях
    for test_file in src_path.rglob("test_*.py"):
        if test_file.is_file():
            process_test_file(test_file)

    print("\n✅ Processing complete!")
