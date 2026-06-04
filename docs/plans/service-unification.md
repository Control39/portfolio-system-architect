# Service Unification Plan

> **Дата:** 18 мая 2026
> **Приоритет:** TIER 2 #3
> **Статус:** Анализ завершён

---

## 📊 Текущее состояние

### Анализ структуры 14 сервисов в `apps/`:

| Сервис | main.py/app.py | src/ | config/ | tests/ | Dockerfile | requirements.txt |
|--------|----------------|------|---------|--------|------------|------------------|
| **ai-config-manager** | ❌ (JS) | ✅ | ✅ | ✅ | ❌ | ✅ |
| **auth_service** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **career_development** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **cognitive-agent** | ✅ (scripts/) | ✅ | ✅ | ✅ | ❌ | ✅ |
| **decision_engine** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **infra-orchestrator** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **it_compass** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **job-automation-agent** | ✅ (job_agent.py) | ✅ | ✅ | ✅ | ❌ | ✅ |
| **knowledge_graph** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **mcp_server** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **ml_model_registry** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **portfolio_organizer** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **system_proof** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **template-service** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **thought-architecture** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

---

## 🔍 Проблемы

### 1. Нестандартные entry points
- `cognitive-agent/`: `scripts/scanner_main.py` вместо `main.py`
- `job-automation-agent/`: `job_agent.py` вместо `main.py`
- `ai-config-manager/`: JavaScript (Electron) вместо Python
- `mcp_server/`: нет main.py
- `ml_model_registry/`: нет main.py
- `portfolio_organizer/`: нет app.py
- `it_compass/`: нет main.py
- `template-service/`: нет ничего

### 2. Отсутствие Dockerfile
- `ai-config-manager/` (JS)
- `cognitive-agent/`
- `job-automation-agent/`
- `template-service/`
- `thought-architecture/`

### 3. Отсутствие requirements.txt
- `template-service/`

---

## 🎯 Целевая структура

### Стандарт Python-сервиса:

```
apps/<service-name>/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI/FastAPI application
│   ├── config.py            # Конфигурация
│   ├── models.py            # Pydantic модели
│   ├── routes/              # API маршруты
│   ├── services/            # Бизнес-логика
│   └── utils/               # Утилиты
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_routes/
│   ├── test_services/
│   └── test_models/
├── config/
│   ├── base.yaml            # Базовая конфигурация
│   ├── dev.yaml             # Dev настройки
│   └── prod.yaml            # Prod настройки
├── Dockerfile               # Стандартизированный образ
├── docker-compose.yml       # (опционально) для локального запуска
├── requirements.txt         # Замороженные зависимости
├── requirements-dev.txt     # Dev зависимости
├── pyproject.toml           # (опционально) для Poetry/pip-tools
├── README.md                # Документация сервиса
├── CHANGELOG.md             # История изменений
├── SECURITY.md              # Инструкции по безопасности
└── .env.example             # Шаблон переменных окружения
```

### Стандарт для agent-сервисов:

```
apps/<agent-name>/
├── src/
│   ├── main.py              # Entry point
│   ├── agent.py             # Логика агента
│   ├── skills/              # Навыки
│   └── workflows/           # Рабочие процессы
├── config/
│   ├── agent.yaml           # Конфиг агента
│   └── triggers.yaml        # Триггеры
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 📋 План унификации

### Шаг 1: Создать шаблон (1 час)

Создать `apps/template/` с идеальной структурой:

```bash
mkdir -p apps/template/{src/{routes,services,utils},tests/{routes,services},config}
```

Шаблонные файлы:
- `src/main.py` — базовый FastAPI app
- `src/config.py` — загрузка конфига
- `Dockerfile` — python:3.11-slim
- `requirements.txt` — базовые зависимости
- `README.md` — шаблон документации

### Шаг 2: Обновить недостающие main.py (2 часа)

| Сервис | Действие |
|--------|----------|
| `it_compass/` | Создать `src/main.py` (Streamlit/FastAPI) |
| `mcp_server/` | Создать `src/main.py` (MCP server) |
| `ml_model_registry/` | Создать `src/main.py` (FastAPI) |
| `portfolio_organizer/` | Создать `src/app.py` (FastAPI) |
| `template-service/` | Создать `src/main.py` + базовые файлы |

### Шаг 3: Добавить Dockerfile (1 час)

| Сервис | Действие |
|--------|----------|
| `cognitive-agent/` | Создать `Dockerfile` |
| `job-automation-agent/` | Создать `Dockerfile` |
| `thought-architecture/` | Создать `Dockerfile` |
| `template-service/` | Создать `Dockerfile` |

### Шаг 4: Стандартизировать config/ (1 час)

Для каждого сервиса:
- Переместить конфиги в `config/`
- Использовать единый формат YAML
- Поддержка `base.yaml`, `dev.yaml`, `prod.yaml`

### Шаг 5: Обновить README (1 час)

Шаблон README.md:
```markdown
# <Service Name>

## Описание
Краткое описание сервиса

## Запуск

### Локально
```bash
pip install -r requirements.txt
python -m src.main
```

### Docker
```bash
docker-compose up -d
```

## API
- `GET /health` — Health check
- `GET /api/v1/...` — Основные endpoints

## Тестирование
```bash
pytest --cov=src
```

## Конфигурация
- `config/base.yaml` — Базовые настройки
- Переменные окружения: `CONFIG_ENV=dev`
```

---

## 🎯 Ожидаемый результат

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| Сервисов с main.py | 9/14 | 14/14 | +5 |
| Сервисов с Dockerfile | 9/14 | 14/14 | +5 |
| Сервисов с config/ | 12/14 | 14/14 | +2 |
| Стандартизированных README | 5/14 | 14/14 | +9 |
| Время разбора нового сервиса | 15 мин | <5 мин | -67% |

---

## ⏱️ Оценка времени

| Задача | Время |
|--------|-------|
| Анализ | ✅ Готово |
| Создание шаблона | 1 час |
| Добавление main.py (5 сервисов) | 2 часа |
| Добавление Dockerfile (4 сервиса) | 1 час |
| Стандартизация config/ | 1 час |
| Обновление README | 1 час |
| Тестирование | 1 час |
| **Всего** | **~7 часов** |

---

## 🚀 Следующие шаги

1. [ ] Создать `apps/template/` с идеальной структурой
2. [ ] Создать main.py для 5 недостающих сервисов
3. [ ] Добавить Dockerfile для 4 сервисов
4. [ ] Стандартизировать config/ во всех сервисах
5. [ ] Обновить README.md во всех сервисах
6. [ ] Создать скрипт генерации нового сервиса
7. [ ] Протестировать все сервисы

---

## 📝 Примечания

- **ai-config-manager/**: JS (Electron) — отдельная структура, не унифицировать
- **cognitive-agent/**: Сложная структура — оставить как есть, добавить Dockerfile
- **template-service/**: Использовать как эталон после создания

---

*Last updated: 18 мая 2026*
