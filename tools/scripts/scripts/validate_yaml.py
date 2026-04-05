#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Валидация YAML-файлов проекта"""

import yaml
import sys
from pathlib import Path

def validate_yaml_files(file_list):
    """Проверяет список YAML-файлов на валидность"""
    errors = []
    
    for filepath in file_list:
        try:
            path = Path(filepath)
            if not path.exists():
                errors.append(f"❌ Файл не найден: {filepath}")
                continue
                
            with open(path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"✅ {filepath}")
            
        except yaml.YAMLError as e:
            errors.append(f"❌ YAML-ошибка в {filepath}: {e}")
        except UnicodeDecodeError as e:
            errors.append(f"❌ Кодировка в {filepath}: {e}")
        except Exception as e:
            errors.append(f"❌ Ошибка в {filepath}: {type(e).__name__}: {e}")
    
    return errors

if __name__ == "__main__":
    # Список файлов для проверки
    yaml_files = [
        'project-config.yaml',
        'documentation-structure.yaml', 
        'code-quality.yaml'
    ]
    
    print("🔍 Валидация YAML-файлов...")
    errors = validate_yaml_files(yaml_files)
    
    if errors:
        print("\n⚠️ Найдены проблемы:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("\n✅ Все YAML-файлы валидны!")
        sys.exit(0)
