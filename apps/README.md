# apps/

> **Микросервисы и приложения проекта.** Каждый сервис — независимый deployable-юнит.
>
> 📋 **Архитектурное правило:** код попадает в `apps/`, если имеет свою точку входа (`main.py`), `Dockerfile` и может быть развёрнут независимо. Подробности в [ADR-015](../architecture/decisions/ADR-015-monorepo-boundary.md).

## 🤖 Автоматическая классификация

Сервисы классифицируются автоматически с помощью [`classify_v4.py`](../../classify_v4.py):

| Критерий | Микросервис | Библиотека |
|----------|-------------|------------|
| **main.py** | ✅ В структуре | ❌ Отсутствует |
| **Dockerfile** | ✅ Есть | ❌ Отсутствует |
| **tests/** | ✅ Есть | ⚠️ Опционально |
| **pyproject.toml** | ⚠️ Опционально | ✅ Обязателен |
| **src/** | ⚠️ Опционально | ✅ Обязателен |

**Пример:**
- `auth_service/` → **микросервис** (98% confidence)
- `cognitive-agent/` → **библиотека** (90% confidence)

📊 **Демо:** [classifier-demo-output.txt](../../docs/reports/classifier-demo-output.txt) — свежий запуск сканера.

> 💡 **Примечание:** Классификация по **технической структуре** (файлы) отличается от **бизнес-классификации** в корневом README (назначение). Оба подхода дополняют друг друга.

## Назначение
- Хранение отдельных приложений и сервисов
- Изоляция логики различных компонентов системы
- Поддержка архитектуры на основе микросервисов
- **Каждое приложение импортирует общие библиотеки из `src/`**, но не из других `apps/`

## Приложения

> **Примечание:** Порты указаны для внутреннего доступа внутри Docker network. Для внешнего доступа используйте маршруты через Traefik (http://localhost[ROUTE]).

| Сервис | Описание | Порт | Маршрут (Traefik) | Dockerfile |
|--------|----------|------|-------------------|------------|
| `auth_service/` | JWT аутентификация и авторизация | 8100 | `/auth` | ✅ |
| `career_development/` | Сервис развития карьеры | 8000 | `/career-dev` | ✅ |
| `cognitive-agent/` | Cognitive Automation Agent | — | — | ✅ |
| `decision_engine/` | RAG + reasoning API | 8001 | `/decision-engine` | ✅ |
| `ml_model_registry/` | ML Model Registry | 8002 | `/ml-registry` | ✅ |
| `infra-orchestrator/` | Оркестратор инфраструктуры | — | — | ✅ |
| `it_compass/` | IT Compass UI (Streamlit) | 8501 | `/it-compass` | ✅ |
| `job-automation-agent/` | Агент автоматизации задач | — | — | ✅ |
| `knowledge_graph/` | Граф знаний | — | — | ✅ |
| `mcp_server/` | MCP сервер для ИИ-агентов | — | — | ✅ |
| `ml_model_registry/` | Реестр ML моделей | 8001 | `/ml-registry` | ✅ |
| `portfolio_organizer/` | Организатор портфолио | 8004 | `/portfolio-organizer` | ✅ |
| `system_proof/` | Система доказательств (CoT) | 8003 | `/system-proof` | ✅ |
| `template-service/` | Шаблон микросервиса | — | — | ✅ |
| `thought-architecture/` | Архитектура мышления | — | — | ✅ |

> **💡 Маршрутизация:** Все сервисы доступны через единый порт (localhost:80). Порты (8001, 8002 и т.д.) используются **внутри** Docker network для маршрутизации через Traefik.

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
