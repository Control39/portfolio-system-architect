"""
Общие утилиты для Cognitive Agent
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any


def calculate_file_hash(file_path: Path) -> str:
    """
    Вычислить хэш файла для определения изменений
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def load_json_file(file_path: Path) -> dict[str, Any] | None:
    """
    Загрузить JSON-файл с обработкой ошибок
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Файл {file_path} не найден")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка парсинга JSON в {file_path}: {e}")
        return None


def find_files_by_extension(directory: Path, extensions: list[str]) -> list[Path]:
    """
    Найти файлы с указанными расширениями в директории
    """
    files = []
    for ext in extensions:
        files.extend(directory.rglob(f"*.{ext.lstrip('.')}"))
    return files


def format_bytes(size_bytes: int) -> str:
    """
    Форматировать размер в байтах в человекочитаемый формат
    """
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f}{size_names[i]}"
