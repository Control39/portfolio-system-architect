# Validate Yaml

- **Путь**: `07_TOOLS\scripts\scripts\validate_yaml.py`
- **Тип**: .PY
- **Размер**: 1,643 байт
- **Последнее изменение**: 2026-03-05 05:17:36

## Превью

```
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
                
            with open(path, 'r', encodin
... (файл продолжается)
```
