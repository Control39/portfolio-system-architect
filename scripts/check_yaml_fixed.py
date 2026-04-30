#!/usr/bin/env python3
"""Проверка всех YAML файлов в проекте на валидность с поддержкой multi-document.
"""

import os
import sys
from pathlib import Path

import yaml


def check_yaml_file(filepath):
    """Проверить один YAML файл (поддерживает multi-document)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Пробуем загрузить как multi-document
        documents = list(yaml.safe_load_all(content))

        # Улучшенная проверка: пустой файл или все документы None (только комментарии)
        if not documents or all(doc is None for doc in documents):
            return False, "Пустой документ или только комментарии"

        # Проверяем, что все документы не None (валидные)
        # Считаем только не-None документы
        valid_docs = [doc for doc in documents if doc is not None]

        if not valid_docs:
            return False, "Нет валидных документов (только комментарии)"

        return (
            True,
            f"OK ({len(valid_docs)} документов, {len(documents) - len(valid_docs)} пустых)",
        )

    except yaml.YAMLError as e:
        return False, f"YAML ошибка: {e}"
    except Exception as e:
        return False, f"Ошибка чтения: {e}"


def find_yaml_files(root_dir):
    """Найти все YAML/yml файлы в проекте."""
    yaml_files = []
    for ext in ("*.yaml", "*.yml"):
        for path in Path(root_dir).rglob(ext):
            # Пропускаем некоторые директории
            str_path = str(path)
            if any(
                ignore in str_path
                for ignore in [
                    ".git",
                    "__pycache__",
                    "node_modules",
                    ".venv",
                    "venv",
                    ".pytest_cache",
                ]
            ):
                continue
            yaml_files.append(path)
    return yaml_files


def main():
    root_dir = "."
    print(f"Поиск YAML файлов в {os.path.abspath(root_dir)}...")

    yaml_files = find_yaml_files(root_dir)
    print(f"Найдено {len(yaml_files)} YAML файлов.")

    errors = []
    for i, filepath in enumerate(yaml_files, 1):
        rel_path = os.path.relpath(filepath, root_dir)
        ok, message = check_yaml_file(filepath)

        if ok:
            print(f"{i:3d}. ✓ {rel_path}: {message}")
        else:
            print(f"{i:3d}. ✗ {rel_path}: {message}")
            errors.append((rel_path, message))

    print("\n" + "=" * 80)
    if errors:
        print(f"НАЙДЕНЫ ОШИБКИ: {len(errors)} файлов с ошибками")
        for rel_path, error in errors[:10]:  # Покажем первые 10 ошибок
            print(f"  - {rel_path}: {error}")
        if len(errors) > 10:
            print(f"  ... и еще {len(errors) - 10} ошибок")
        return 1
    print("ВСЕ YAML ФАЙЛЫ ВАЛИДНЫ!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
