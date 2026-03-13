#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для поиска дублирующихся файлов в директории проекта по хешу содержимого.
Рекурсивно обходит все поддиректории, игнорируя системные директории.
Выводит таблицу с названием файла, содержимым и путем для найденных дубликатов.
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict

# Установка кодировки для корректного отображения кириллицы в консоли Windows
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def get_ignore_patterns():
    """Возвращает список паттернов для игнорирования"""
    return {
        '.git', '__pycache__', '.vscode', '.idea', 'node_modules', '.svn', '.hg',
        '.tox', '.eggs', '*.egg-info', '.pytest_cache', '.coverage',
        '.mypy_cache', '.ruff_cache', '.cache'
    }


def should_ignore(path, ignore_patterns):
    """
    Проверяет, следует ли игнорировать указанный путь
    
    Args:
        path (str): Путь к файлу или директории
        ignore_patterns (set): Множество паттернов для игнорирования
        
    Returns:
        bool: True, если путь должен быть проигнорирован, иначе False
    """
    path_obj = Path(path)
    
    # Проверяем каждую часть пути
    for part in path_obj.parts:
        if part in ignore_patterns:
            return True
            
    return False


def scan_directory(root_path, ignore_patterns):
    """
    Рекурсивно сканирует директорию и возвращает список путей к файлам
    
    Args:
        root_path (str): Корневая директория для сканирования
        ignore_patterns (set): Множество паттернов для игнорирования
        
    Returns:
        list: Список путей к файлам
    """
    file_paths = []
    
    try:
        # Используем os.walk для рекурсивного обхода директорий
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Фильтруем директории для игнорирования
            dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), ignore_patterns)]
            
            # Обрабатываем файлы в текущей директории
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                # Проверяем, следует ли игнорировать файл
                if not should_ignore(file_path, ignore_patterns):
                    # Проверяем размер файла (пропускаем файлы нулевой длины)
                    try:
                        if os.path.getsize(file_path) > 0:
                            file_paths.append(file_path)
                    except (OSError, IOError):
                        # Пропускаем файлы, к которым нет доступа
                        print(f"Предупреждение: Нет доступа к файлу {file_path}")
                        continue
                        
    except (OSError, IOError) as e:
        print(f"Ошибка при сканировании директории {root_path}: {e}")
        
    return file_paths


def calculate_file_hash(file_path, block_size=8192):
    """
    Вычисляет SHA256 хеш содержимого файла
    
    Args:
        file_path (str): Путь к файлу
        block_size (int): Размер блока для чтения файла
        
    Returns:
        str: SHA256 хеш файла или None в случае ошибки
    """
    hash_sha256 = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            # Читаем файл блоками для эффективного использования памяти
            for block in iter(lambda: f.read(block_size), b""):
                hash_sha256.update(block)
        return hash_sha256.hexdigest()
    except (OSError, IOError) as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
        return None


def find_duplicates(file_paths):
    """
    Находит дубликаты файлов по хешу содержимого
    
    Args:
        file_paths (list): Список путей к файлам
        
    Returns:
        dict: Словарь {hash: [file_paths]} для файлов-дубликатов
    """
    hash_to_files = defaultdict(list)
    
    # Вычисляем хеши для всех файлов
    for file_path in file_paths:
        file_hash = calculate_file_hash(file_path)
        if file_hash:
            hash_to_files[file_hash].append(file_path)
    
    # Фильтруем только дубликаты (группы с более чем одним файлом)
    duplicates = {hash_val: paths for hash_val, paths in hash_to_files.items() if len(paths) > 1}
    
    return duplicates


def get_file_preview(file_path, max_length=100):
    """
    Возвращает превью содержимого файла (первые max_length символов)
    
    Args:
        file_path (str): Путь к файлу
        max_length (int): Максимальная длина превью
        
    Returns:
        str: Превью содержимого файла
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(max_length)
            # Заменяем символы новой строки на пробелы для лучшего отображения
            content = content.replace('\n', ' ').replace('\r', ' ')
            return content
    except (OSError, IOError):
        return "[Невозможно прочитать содержимое]"


def display_duplicates(duplicates):
    """
    Выводит дубликаты в виде таблицы
    
    Args:
        duplicates (dict): Словарь {hash: [file_paths]} дубликатов
    """
    if not duplicates:
        print("Дубликаты не найдены.")
        return
    
    print(f"\nНайдено {len(duplicates)} групп дубликатов:\n")
    
    # Заголовок таблицы
    print(f"{'Название файла':<30} {'Содержимое (первые 100 символов)':<50} {'Путь к файлу':<50}")
    print("-" * 130)
    
    # Выводим информацию о каждом дубликате
    for i, (file_hash, file_paths) in enumerate(duplicates.items(), 1):
        print(f"\nГруппа {i} (Хеш: {file_hash[:16]}...):")
        print("=" * 130)
        
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            preview = get_file_preview(file_path)
            
            # Форматируем строки для лучшего отображения
            filename_display = filename[:28] + "…" if len(filename) > 28 else filename
            preview_display = preview[:48] + "…" if len(preview) > 48 else preview
            path_display = file_path[:48] + "…" if len(file_path) > 48 else file_path
            
            print(f"{filename_display:<30} {preview_display:<50} {path_display:<50}")


def main():
    """Основная функция скрипта"""
    # Установка кодировки UTF-8 для корректного отображения кириллицы
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description="Поиск дубликатов файлов по хешу содержимого")
    parser.add_argument("path", nargs="?", default=".", help="Путь к директории для сканирования (по умолчанию текущая директория)")
    args = parser.parse_args()
    
    root_path = os.path.abspath(args.path)
    
    if not os.path.exists(root_path):
        print(f"Ошибка: Директория {root_path} не существует")
        return
    
    if not os.path.isdir(root_path):
        print(f"Ошибка: {root_path} не является директорией")
        return
    
    print(f"Сканирование директории: {root_path}")
    
    # Получаем паттерны для игнорирования
    ignore_patterns = get_ignore_patterns()
    
    # Сканируем директорию
    print("Сканирование файлов...")
    file_paths = scan_directory(root_path, ignore_patterns)
    print(f"Найдено {len(file_paths)} файлов для анализа")
    
    if not file_paths:
        print("Нет файлов для анализа.")
        return
    
    # Ищем дубликаты
    print("Поиск дубликатов...")
    duplicates = find_duplicates(file_paths)
    
    # Выводим результаты
    display_duplicates(duplicates)


if __name__ == "__main__":
    main()