# apps/

> **Микросервисы и приложения проекта.** Каждый сервис — независимый deployable-юнит.
>
> 📋 **Архитектурное правило:** код попадает в `apps/`, если имеет свою точку входа (`main.py`), `Dockerfile` и может быть развёрнут независимо. Подробности в [ADR-015](../architecture/decisions/ADR-015-monorepo-boundary.md).

## Назначение
- Хранение отдельных приложений и сервисов
- Изоляция логики различных компонентов системы
- Поддержка архитектуры на основе микросервисов
- **Каждое приложение импортирует общие библиотеки из `src/`**, но не из других `apps/`

## Приложения

| Сервис | Описание | Порт | Dockerfile |
|--------|----------|------|------------|
| `auth_service/` | JWT аутентификация и авторизация | 8100 | ✅ |
| `career_development/` | Сервис развития карьеры | 8000 | ⚠️ отсутствует |
| `cognitive-agent/` | Cognitive Automation Agent | — | ✅ |
| `decision-engine/` | RAG + reasoning API | 8001 | ✅ |
| `infra-orchestrator/` | Оркестратор инфраструктуры | — | ✅ |
| `it_compass/` | IT Compass UI (Streamlit) | 8501 | ✅ |
| `job-automation-agent/` | Агент автоматизации задач | — | ✅ |
| `knowledge-graph/` | Граф знаний | — | ✅ |
| `mcp-server/` | MCP сервер для ИИ-агентов | — | ✅ |
| `ml-model-registry/` | Реестр ML моделей | 8001 | ✅ |
| `portfolio_organizer/` | Организатор портфолио | 8004 | ✅ |
| `system-proof/` | Система доказательств (CoT) | 8003 | ✅ |
| `template-service/` | Шаблон микросервиса | — | ✅ |
| `thought-architecture/` | Архитектура мышления | — | ✅ |

## Зависимости от `src/`

Микросервисы импортируют общие компоненты из корневого `src/`:

```python
# Пример из apps/auth_service/main.py
from src.common.health_check import init_health_checks

# Пример из apps/ml-model-registry/src/main.py
from src.common.health_check import init_health_checks
from src.common.async_helpers import fetch_parallel
```

## Внутренняя структура сервиса

Каждый сервис может иметь **собственный** `src/` — это его внутренняя организация, не связанная с корневым `src/`:

```
apps/template-service/
├── src/              ← внутренний src сервиса
│   ├── api/
│   └── core/
├── Dockerfile
└── requirements.txt
```

> **Важно:** импорты вида `from src.api import router` внутри `apps/*/src/main.py` относятся к **внутреннему** `src` сервиса.

## Архитектурные правила

- ✅ Каждый сервис имеет `Dockerfile` (кроме `career_development` — требуется добавить)
- ✅ Сервисы не импортируют код друг из друга напрямую — только через API
- ✅ Общие библиотеки импортируются из корневого `src/`
- ❌ `src/` не импортирует код из `apps/`
