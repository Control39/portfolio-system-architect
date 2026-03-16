# Reasoning Api

- **Путь**: `components\portfolio-organizer\src\api\reasoning_api.py`
- **Тип**: .PY
- **Размер**: 6,629 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
"""
API для анализа и рекомендаций по проектам портфолио
"""

from flask import Flask, jsonify, request
from typing import Dict, List, Any
import json
import os

app = Flask(__name__)

# Демонстрационные данные проектов
SAMPLE_PROJECTS = [
    {
        "id": 1,
        "name": "E-commerce Platform",
        "description": "Платформа для онлайн-торговли с полным набором функций",
        "status": "in-progress",
        "progress": 75,
        "deadline": "2026-03-15",
        "technologies": ["
... (файл продолжается)
```
