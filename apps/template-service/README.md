# Template Service

Шаблон микросервиса для проекта portfolio-system-architect.

Этот шаблон предоставляет стандартизированную структуру для создания новых микросервисов в экосистеме portfolio-system-architect.

## Структура проекта

```
template-service/
├── Dockerfile              # Многоступенчатый Dockerfile
├── pyproject.toml          # Зависимости и конфигурация инструментов
├── config.yaml             # Конфигурация в формате YAML
├── .env.example            # Пример переменных окружения
├── src/                    # Исходный код
│   ├── __init__.py
│   ├── main.py             # Точка входа приложения
│   ├── api/                # API endpoints
│   │   ├── __init__.py
│   │   └── router.py       # Основной роутер API
│   ├── core/               # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py       # Конфигурация
│   │   ├── database.py     # Работа с базой данных
│   │   └── health.py       # Health check endpoints
│   ├── models/             # Модели данных
│   │   └── __init__.py
│   └── utils/              # Вспомогательные утилиты
│       └── __init__.py
└── tests/                  # Тесты
    └── test_health.py      # Тесты health check
```

## Быстрый старт

### 1. Клонирование шаблона

```bash
# Скопируйте шаблон в новый микросервис
cp -r apps/template-service apps/my-new-service
cd apps/my-new-service
```

### 2. Настройка окружения

```bash
# Скопируйте пример переменных окружения
cp .env.example .env

# Отредактируйте .env под свои нужды
# Установите DATABASE_URL, REDIS_URL и другие параметры
```

### 3. Установка зависимостей

```bash
# Установка зависимостей для разработки
pip install -e .[dev]

# Или только основных зависимостей
pip install -e .
```

### 4. Запуск сервиса

```bash
# Запуск в режиме разработки
python -m src.main

# Или через uvicorn напрямую
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Проверка работоспособности

```bash
# Health check
curl http://localhost:8000/health/

# Документация API (если DEBUG=true)
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Docker

### Сборка образа

```bash
docker build -t template-service:latest .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  -e REDIS_URL=redis://host:6379/0 \
  template-service:latest
```

## Конфигурация

### Переменные окружения

Основные переменные окружения:

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `TEMPLATE_ENVIRONMENT` | Окружение (development/staging/production) | `development` |
| `TEMPLATE_DEBUG` | Режим отладки | `true` |
| `TEMPLATE_HOST` | Хост для сервера | `0.0.0.0` |
| `TEMPLATE_PORT` | Порт для сервера | `8000` |
| `TEMPLATE_DATABASE_URL` | URL базы данных PostgreSQL | `postgresql://user:password@localhost:5432/template_db` |
| `TEMPLATE_REDIS_URL` | URL Redis | `redis://localhost:6379/0` |
| `TEMPLATE_SECRET_KEY` | Секретный ключ для JWT | `change-this-in-production` |

### Конфигурационные файлы

- `.env` - переменные окружения (не коммитить!)
- `config.yaml` - конфигурация в YAML формате
- `pyproject.toml` - зависимости и настройки инструментов

## Разработка

### Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск тестов с покрытием
pytest --cov=src --cov-report=term-missing --cov-report=xml

# Запуск конкретного теста
pytest tests/test_health.py -v
```

### Линтинг и форматирование

```bash
# Проверка форматирования Black
black --check .

# Автоформатирование
black .

# Линтинг с Ruff
ruff check .

# Проверка типов с mypy
mypy src/
```

### Pre-commit hooks

```bash
# Установка pre-commit hooks
pre-commit install

# Запуск на всех файлах
pre-commit run --all-files
```

## Интеграция с CI/CD

Шаблон совместим с консолидированным CI/CD workflow проекта:

- Автоматические тесты при push/pull request
- Проверка безопасности
- Сборка Docker образов
- Развертывание в Kubernetes

## Мониторинг

Сервис предоставляет следующие endpoints для мониторинга:

- `GET /health/` - базовый health check
- `GET /health/ready` - readiness check (проверяет зависимости)
- `GET /health/live` - liveness check для Kubernetes

## Логирование

Используется Loguru для структурированного логирования. Уровень логирования настраивается через `LOG_LEVEL`.

## Безопасность

- CORS настроен через `CORS_ORIGINS`
- JWT для аутентификации (настраивается через `SECRET_KEY`)
- Переменные окружения для чувствительных данных
- Проверка безопасности в CI/CD pipeline

## Лицензия

MIT