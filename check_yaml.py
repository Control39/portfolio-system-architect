#!/usr/bin/env python3
"""
Проверка всех YAML файлов в проекте на валидность.
"""

import yaml
import os
import sys
from pathlib import Path

def check_yaml_file(filepath):
    """Проверить один YAML файл."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            yaml.safe_load(content)
        return True, None
    except yaml.YAMLError as e:
        return False, f"YAML ошибка: {e}"
    except Exception as e:
        return False, f"Ошибка чтения: {e}"

def find_yaml_files(root_dir):
    """Найти все YAML/yml файлы в проекте."""
    yaml_files = []
    for ext in ('*.yaml', '*.yml'):
        for path in Path(root_dir).rglob(ext):
            # Пропускаем некоторые директории
            str_path = str(path)
            if any(ignore in str_path for ignore in [
                '.git', '__pycache__', 'node_modules', 
                '.venv', 'venv', '.pytest_cache'
            ]):
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
        ok, error = check_yaml_file(filepath)
        
        if ok:
            print(f"{i:3d}. ✓ {rel_path}")
        else:
            print(f"{i:3d}. ✗ {rel_path}: {error}")
            errors.append((rel_path, error))
    
    print("\n" + "="*80)
    if errors:
        print(f"НАЙДЕНЫ ОШИБКИ: {len(errors)} файлов с ошибками")
        for rel_path, error in errors:
            print(f"  - {rel_path}: {error}")
        return 1
    else:
        print("ВСЕ YAML ФАЙЛЫ ВАЛИДНЫ!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
