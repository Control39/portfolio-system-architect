# Helpers

- **Путь**: `components\career-development-system\src\utils\helpers.py`
- **Тип**: .PY
- **Размер**: 3,268 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
import json
import os
from datetime import datetime


def load_json_file(filepath):
    """Загрузить данные из JSON файла"""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {filepath} не найден")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка декодирования JSON в файле {filepath}")
        return None


def save_json_file(filepath, data):
    """Сохранить данные
... (файл продолжается)
```
