# Portfolio Integration

- **Путь**: `components\ml-model-registry\src\api\portfolio_integration.py`
- **Тип**: .PY
- **Размер**: 14,004 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
"""
Модуль интеграции между ML Model Registry и Portfolio Organizer.

Обеспечивает двусторонний обмен данными между сервисами.
Поддерживает экспорт моделей, получение информации и синхронизацию статусов.
"""
import os
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Request
import httpx
from pydantic import BaseModel

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(prefix="/portf
... (файл продолжается)
```
