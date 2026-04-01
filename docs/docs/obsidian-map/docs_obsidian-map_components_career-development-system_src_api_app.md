# Components Career Development System Src Api App

- **Путь**: `docs\obsidian-map\components_career-development-system_src_api_app.md`
- **Тип**: .MD
- **Размер**: 811 байт
- **Последнее изменение**: 2026-03-12 10:52:56

## Превью

```
# App

- **Путь**: `components\career-development-system\src\api\app.py`
- **Тип**: .PY
- **Размер**: 16,224 байт
- **Последнее изменение**: 2026-03-08 16:11:38

## Превью

```
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///career_dev.db"
)
db = SQLAlchemy(app)


# Модель пользователя
class User(db.Model)
... (файл продолжается)
```

