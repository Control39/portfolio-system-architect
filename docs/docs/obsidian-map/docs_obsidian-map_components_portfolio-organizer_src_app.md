# Components Portfolio Organizer Src App

- **Путь**: `docs\obsidian-map\components_portfolio-organizer_src_app.md`
- **Тип**: .MD
- **Размер**: 936 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# App

- **Путь**: `components\portfolio-organizer\src\app.py`
- **Тип**: .PY
- **Размер**: 1,766 байт
- **Последнее изменение**: 2026-03-10 19:02:48

## Превью

```
"""
Основное приложение Portfolio Organizer.
Объединяет все API модули.
"""

from flask import Flask
from api.reasoning_api import app as reasoning_app
from api.ml_model_registry_integration import bp as ml_model_registry_bp

app = Flask(__name__)

# Регистрируем blueprint для интеграции с ML Model Registry
app.register_blueprint(ml
... (файл продолжается)
```
