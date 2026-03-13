# Ml Model Registry Integration

- **Путь**: `02_MODULES\portfolio-organizer\portfolio-organizer\src\api\ml_model_registry_integration.py`
- **Тип**: .PY
- **Размер**: 4,177 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
"""
Интеграция с ML Model Registry для Portfolio Organizer.
Предоставляет эндпоинты для взаимодействия с реестром моделей.
"""

from flask import Blueprint, jsonify, request
import requests
import os

bp = Blueprint('ml_model_registry', __name__, url_prefix='/api/ml-model-registry')

# Конфигурация
ML_MODEL_REGISTRY_URL = os.environ.get(
    'ML_MODEL_REGISTRY_URL',
    'http://localhost:8000'
)

@bp.route('/models', methods=['GET'])
def list_models():
    """Получение списка моделей из ML Model
... (файл продолжается)
```
