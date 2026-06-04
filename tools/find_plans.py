#!/usr/bin/env python3
"""Найти все файлы планов в скрытых директориях"""

import os


def find_files(base_dir, pattern):
    """Рекурсивно найти файлы по паттерну"""
    if not os.path.exists(base_dir):
        print(f"Папка {base_dir} не существует")
        return

    print(f"\n=== {base_dir} ===")
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(pattern):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, ".")
                print(rel_path)


# Найти планы
find_files(".koda", ".md")
find_files(".reports", ".md")
find_files(".gigacode", ".plan.md")
find_files(".agents", ".md")
find_files(".sourcecraft", ".md")
