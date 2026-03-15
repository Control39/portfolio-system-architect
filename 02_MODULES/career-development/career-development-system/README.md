# Career Development System

Система управления карьерным развитием на основе **объективных маркеров компетенций**.  

## Основные компоненты
- **FastAPI‑backend** (`src/api/app.py`) – CRUD‑операции для профилей, целей, маркеров.
- **React‑SPA** (`src/web/index.html`) – веб‑дашборд.
- **React‑Native** (`src/mobile/app.js`) – мобильный клиент.
- **Core‑логика** (`src/core/`) – трекер маркеров, Pydantic‑модели.
- **utils** – вспомогательные функции (генерация UUID, валидация ссылок).

## Как начать
1. Установите зависимости из `requirements.txt` (в `02_MODULES/cloud-reason` уже есть нужные пакеты).  
2. Запустите миграцию (если используете SQLite/PostgreSQL).  
3. `uvicorn src.api.app:app --reload` – запустит API на `http://localhost:8000`.  
4. Откройте `src/web/index.html` в браузере – увидите простой дашборд.

Для более подробного описания API смотрите `docs/API_REFERENCE.md` и `src/docs/api_documentation.md`.  

