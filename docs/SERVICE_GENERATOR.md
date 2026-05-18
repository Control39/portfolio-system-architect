# Генератор сервисов — Руководство

> **Версия:** 1.0.0  
> **Дата:** 18 мая 2026 г.

---

## 🎯 Назначение

Автоматическое создание новых микросервисов из шаблона `template-service` с полной структурой, тестами и документацией.

---

## 🚀 Использование

### Базовое создание

```bash
python scripts/create_service.py <service-name> --description "Описание сервиса"
```

**Примеры:**

```bash
# Создать сервис с описанием
python scripts/create_service.py user-service --description="Управление пользователями"

# Создать сервис без описания (по умолчанию: "Новый сервис")
python scripts/create_service.py payment-api
```

### Дополнительные опции

```bash
python scripts/create_service.py <service-name> --description "..." --add-compose
```

**`--add-compose`** — автоматически добавить сервис в `docker-compose.yml`

---

## 📁 Что создаётся

### Структура сервиса

```
apps/<service-name>/
├── main.py                 # Entry point (FastAPI app)
├── README.md              # Документация (7 секций)
├── requirements.txt       # Зависимости
├── Dockerfile            # Контейнеризация
├── .dockerignore         # Исключения Docker
├── .gitignore            # Исключения Git
├── __init__.py
│
├── src/                  # Исходный код
│   ├── __init__.py
│   ├── core/            # Ядро сервиса
│   │   └── __init__.py
│   ├── api/             # API endpoints
│   │   └── __init__.py
│   └── utils/           # Вспомогательные функции
│
└── tests/               # Тесты
    ├── __init__.py
    └── test_main.py     # Базовые тесты (2 теста)
```

### Содержимое файлов

#### main.py
- FastAPI приложение с title, description, version
- Эндпоинты `/health` и `/`
- Готово к запуску через uvicorn

#### README.md
Все 7 обязательных секций:
1. Purpose
2. Features
3. API (таблица эндпоинтов)
4. Dependencies
5. Deployment
6. Contributing

#### tests/test_main.py
- `test_health_check()` — проверка /health
- `test_root()` — проверка /

---

## 📋 Следующие шаги после создания

```bash
# 1. Перейти в директорию сервиса
cd apps/<service-name>

# 2. Добавить бизнес-логику
# Отредактируйте:
# - src/core/ — ядро сервиса
# - src/api/ — API endpoints
# - main.py — роутинг

# 3. Обновить README.md
# Добавьте детали, примеры использования, схемы данных

# 4. Запустить тесты
python -m pytest

# 5. Запустить сервис локально
python main.py

# Или через Docker
docker-compose up <service-name>
```

---

## 🔧 Настройка шаблона

### Изменить базовые зависимости

Отредактируйте `scripts/create_service.py`, секция `templates["requirements.txt"]`:

```python
"requirements.txt": """fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pytest>=7.0.0
# Добавить новые зависимости
httpx>=0.24.0
aioredis>=2.0.0
""",
```

### Изменить базовую структуру

Отредактируйте `scripts/create_service.py`, секция `dirs`:

```python
dirs = [
    "src",
    "src/core",
    "src/api",
    "src/utils",
    "src/models",      # Добавить
    "tests",
    "tests/integration"  # Добавить
]
```

### Изменить базовые тесты

Отредактируйте `scripts/create_service.py`, секция `test_content`:

```python
test_content = f'''"""Тесты для {sanitized_name}."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Проверка эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "{sanitized_name}"


def test_root():
    """Проверка корневой страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "{sanitized_name}"
    assert "version" in response.json()


# Добавить дополнительные тесты
def test_custom_endpoint():
    """Пример кастомного теста."""
    response = client.get("/custom")
    assert response.status_code == 200
'''
```

---

## ✅ Автоматическая проверка

После создания сервиса он автоматически проходит проверку:

```bash
# Запустить проверку структуры
python scripts/check_service_structure.py --service <service-name>

# Ожидается:
# ✅ Соответствует: <service-name> (100%)
```

---

## 🚨 Устранение проблем

### Ошибка: "Сервис уже существует"

```
❌ Ошибка: Сервис 'my-service' уже существует
```

**Решение:** Удалите существующий сервис или используйте другое имя.

### Ошибка: "docker-compose.yml не найден"

```
⚠️  docker-compose.yml не найден, пропуск
```

**Решение:** Это предупреждение, не ошибка. Сервис создан, просто не добавлен в docker-compose.

### Тесты не проходят

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
python -m pytest -v
```

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Время создания сервиса | ~2 сек |
| Файлов создано | 14 |
| Директорий создано | 8 |
| Тестов включено | 2 |
| Покрытие тестами (базовое) | 100% |

---

## 📚 Примеры использования

### Пример 1: API для управления задачами

```bash
python scripts/create_service.py task-api --description="REST API для управления задачами"

# Результат:
# apps/task-api/
# ├── main.py (с health check и root)
# ├── README.md (7 секций)
# ├── src/
# │   ├── core/ (бизнес-логика задач)
# │   └── api/ (endpoints: GET/POST/PUT/DELETE /tasks)
# └── tests/
#     └── test_main.py (2 базовых теста)
```

### Пример 2: Фоновый воркер

```bash
python scripts/create_service.py background-worker --description="Фоновая обработка задач"

# После создания:
# - Измените main.py на asyncio worker
# - Добавьте Celery/RQ в requirements.txt
# - Добавьте тесты для воркера
```

### Пример 3: Микросервис с БД

```bash
python scripts/create_service.py user-service --description="Управление пользователями"

# После создания:
# - Добавьте SQLAlchemy в requirements.txt
# - Создайте src/models/user.py
# - Добавьте миграции Alembic
# - Обновите README с схемой БД
```

---

## 🔗 Ссылки

- [Стандарт структуры сервиса](../docs/SERVICE_STRUCTURE_STANDARD.md)
- [Шаблон сервиса](../apps/template-service/)
- [Проверка структуры](../scripts/check_service_structure.py)
- [Docker Compose](../docker-compose.yml)

---

*Последнее обновление: 18 мая 2026 г.*
