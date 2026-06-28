#!/usr/bin/env python3
"""Исправление сгенерированных тестов"""

import re
from pathlib import Path


def fix_extract_port_from_config_test(test_content: str) -> str:
    """
    Исправить тесты extract_port_from_config - они должны мокать COMPONENT_CONFIG в модуле src.main
    """
    # Паттерн для замены mocker.patch.dict на mocker.patch с правильным target
    old_pattern = r"mocker\.patch\.dict\(COMPONENT_CONFIG,"
    new_pattern = "mocker.patch('src.main.COMPONENT_CONFIG', new="

    test_content = re.sub(old_pattern, new_pattern, test_content)

    # Дополнительно: исправить параметры
    # Заменить config на dict
    test_content = re.sub(
        r"def test_extract_port_from_config_valid_script\(config, mocker\):",
        "def test_extract_port_from_config_valid_script(mocker):",
        test_content,
    )

    return test_content


def fix_main_tests(test_content: str) -> str:
    """
    Исправить тесты main/main_dev/main_prod - они должны мокать uvicorn.run
    """
    # Добавить мок uvicorn.run ко всем тестам, которые вызывают main* функции
    # Проверить, есть ли already импорт uvicorn
    if "from unittest.mock import patch" in test_content:
        # already有 patch
        pass
    elif "from unittest.mock import" in test_content:
        # Add to existing import
        test_content = re.sub(r"from unittest\.mock import (.+)", r"from unittest.mock import \1, patch", test_content)
    else:
        # Add new import
        test_content = re.sub(r"(import pytest)", r"from unittest.mock import patch\n\n\1", test_content)

    return test_content


def fix_test_file(file_path: Path) -> None:
    """Исправить один файл с тестами"""
    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Применить исправления
    content = fix_extract_port_from_config_test(content)
    content = fix_main_tests(content)

    # Сохранить, если были изменения
    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"✓ Fixed: {file_path}")
    else:
        print(f"- No changes: {file_path}")


if __name__ == "__main__":
    # Обработать все тестовые файлы в src/
    src_path = Path("C:/repo/src")

    for test_file in src_path.glob("test_*.py"):
        if test_file.is_file():
            fix_test_file(test_file)

    # Также в поддиректориях
    for test_file in src_path.rglob("test_*.py"):
        if test_file.is_file():
            fix_test_file(test_file)

    print("\n✅ Fixing complete!")
