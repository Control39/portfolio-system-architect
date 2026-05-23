# apps/

> **Микросервисы и приложения проекта.** Каждый сервис — независимый deployable-юнит.
>
> 📋 **Архитектурное правило:** код попадает в `apps/`, если имеет свою точку входа (`main.py`), `Dockerfile` и может быть развёрнут независимо. Подробности в [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md).

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

## 🚀 Доступ к сервисам

> **⚠️ Важное примечание:** В текущей реализации (Windows/Docker Desktop) используется **прямой доступ по портам** из-за проблем с Docker socket в Traefik. Traefik routing временно не работает.
>
> **Почему так:** Traefik требует mount `/var/run/docker.sock` для auto-discovery сервисов. В Windows Docker Desktop это работает нестабильно (см. `.reports/traefik-routing-analysis.md`).
>
> **План:** При достижении 5+ сервисов или переходе на production — внедрение nginx/Traefik (см. `.koda/plans/traefik-decision-plan.md`).

### Прямые порты (текущая конфигурация)

| Сервис | Порт | Health Check | Статус |
|--------|------|--------------|--------|
| `auth_service/` | 8100 | `http://localhost:8100/health` | ✅ |
| `career_development/` | 8000 | `http://localhost:8000/health` | ✅ |
| `decision_engine/` | 8001 | `http://localhost:8001/api/v1/status` | ✅ |
| `ml_model_registry/` | 8002 | `http://localhost:8002/health` | ✅ |
| `system_proof/` | 8003 | `http://localhost:8003/health` | ✅ |
| `portfolio_organizer/` | 8004 | `http://localhost:8004/health` | ✅ |
| `it_compass/` | 8501 | `http://localhost:8501/_stcore/health` | ✅ |
| `infra-orchestrator/` | 8005 | `http://localhost:8005/health` | ✅ |
| `job-automation-agent/` | 8006 | `http://localhost:8006/health` | ✅ |
| `knowledge_graph/` | 8007 | `http://localhost:8007/health` | ✅ |
| `mcp_server/` | 8008 | `http://localhost:8008/health` | ✅ |
| `thought-architecture/` | 8009 | `http://localhost:8009/health` | ✅ |
| `ai-config-manager/` | 8010 | `http://localhost:8010/health` | ✅ |
| `cognitive-agent/` | — | CLI (без порта) | ✅ |

### Маршруты через Traefik (недоступны в Windows)

| Сервис | Маршрут | Порт | Статус |
|--------|---------|------|--------|
| `auth_service/` | `/auth` | 8100 | ❌ 404 |
| `decision_engine/` | `/decision-engine` | 8001 | ❌ 404 |
| `ml_model_registry/` | `/ml-registry` | 8002 | ❌ 404 |
| `system_proof/` | `/system-proof` | 8003 | ❌ 404 |
| `portfolio_organizer/` | `/portfolio-organizer` | 8004 | ❌ 404 |
| `it_compass/` | `/it-compass` | 8501 | ❌ 404 |
| `career_development/` | `/career-dev` | 8000 | ❌ 404 |

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
