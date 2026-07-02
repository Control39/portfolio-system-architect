# src/ — Общие компоненты (Атомы)

> **Централизованные библиотеки и ядро системы.**
> Импортируются микросервисами из `apps/`.
>
> 📋 **Архитектурное правило:** код попадает в `src/`, если используется **двумя и более** приложениями из `apps/`.
> Подробности в [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md).
>
> **Обновлено:** 2026-07-02

---

## Обзор

`src/` — это **атомы архитектуры**, обеспечивающие повторное использование кода между сервисами.
Каждый атом независим и может использоваться любым микросервисом без обратных зависимостей.

---

## Статистика

| Категория | Количество |
|-----------|------------|
| **Атомов (модули)** | 10 |
| **Интеграций** | 21+ сервисов |
| **Ключевых функций** | 50+ |

---

## Назначение

- ✅ Централизованное расположение общих библиотек и утилит
- ✅ Обеспечение повторного использования кода между приложениями
- ❌ **Запрещено** импортировать код из `apps/` — `src/` должен быть независимым
- ✅ Полное покрытие тестами (≥75%)

---

## Структура — 10 атомов

| Модуль | Описание | Типичные импортеры |
|--------|----------|-------------------|
| `ai/` | Компоненты ИИ (GigaChat, Ollama bridge) | `decision-engine`, `cognitive-agent` |
| `common/` | Общие утилиты (`health_check`, `async_helpers`) | Все сервисы |
| `config/` | Загрузка и валидация конфигураций | Все сервисы |
| `core/` | Базовые интерфейсы и абстракции | Все сервисы |
| `infrastructure/` | Управление инфраструктурой | `infra-orchestrator` |
| `interfaces/` | Интерфейсы интеграции (Job Search, IT Compass) | `job-automation-agent`, `it-compass` |
| `security/` | Безопасность (маскирование секретов, rate limiting) | Все сервисы |
| `shared/` | Общие библиотеки, LLM-клиенты, Pydantic-модели | Все сервисы |
| `vector_store/` | ChromaDB RAG, векторные запросы | `cognitive-agent`, `knowledge-graph` |

> 📦 **Архив устаревших модулей:** `decision_engine_v1/`, `repo_audit_v1/` перемещены в [`legacy/`](../legacy/).
> История коммитов сохранена (`git mv`).

---

## Ключевые модули

### common/ — Общие утилиты

```python
from src.common.health_check import HealthChecker
from src.common.async_helpers import async_retry, TimeoutError

# Пример использования
checker = HealthChecker()
is_healthy = checker.check("my-service")
```

### security/ — Безопасность

```python
from src.security.enterprise_guardrails import EnterpriseGuardrails, UserRole, AccessLevel
from src.security.rate_limiter import PredefinedRateLimiters

# Пример использования
guardrails = EnterpriseGuardrails()
token = guardrails.authenticate_user(user_id="user-123", role=UserRole.DEVELOPER)

rate_limiter = PredefinedRateLimiters.ai_calls()
rate_limiter.check_rate_limit("ai:user-123")
```

### vector_store/ — RAG и векторы

```python
from src.vector_store.chroma_impl import ChromaDocumentIndexer
from src.vector_store.embedder import DocumentEmbedder

indexer = ChromaDocumentIndexer(
    persist_directory="./chroma_db",
    collection_name="project_docs",
    embedder=DocumentEmbedder()
)

indexer.add_documents(documents)
results = indexer.search(query="архитектура агента")
```

### shared/ — Общие модели

```python
from src.shared.models import CareerProof, SkillMarker
from src.shared.llm.client import LLMClient

# Пример использования
client = LLMClient()
response = client.generate_text(prompt="Опиши архитектуру", system_message="Ты — архитектор")
```

---

## Импортирование модулей

Используйте **абсолютные импорты** для обеспечения независимости:

```python
# ✅ Правильно
from src.common.health_check import HealthChecker
from src.security.rate_limiter import RateLimitExceededError
from src.vector_store.chroma_impl import ChromaDocumentIndexer

# ❌ Неправильно (relative import)
from .common.health_check import HealthChecker
```

---

## Ключевые импортеры (из `apps/`)

| Модуль `src/` | Используется в |
|---------------|---------------|
| `src.common.health_check` | `auth_service`, `ml-model-registry`, `job-automation-agent`, `decision-engine` |
| `src.common.async_helpers` | `ml-model-registry`, `job-automation-agent` |
| `src.embedding_agent` | `mcp-server` (опционально) |
| `src.config` | тесты, скрипты |

---

## Тестирование

```bash
# Запуск тестов для атомов
pytest src/*/tests/ -v

# С coverage
pytest src/*/tests/ --cov=src --cov-report=term-missing

# Тесты конкретного атома
pytest src/security/tests/ -v
pytest src/vector_store/tests/ -v
```

---

## ✅ Решённые проблемы

- ~~`src/decision_engine/`~~ → архивировано в `legacy/decision_engine_v1/`
- ~~`src/repo_audit/`~~ → архивировано в `legacy/repo_audit_v1/`

> Активные версии: `apps/decision-engine/` и `tools/repo_audit/`.

---

## Архитектурные принципы

1. **Один атом — одна ответственность**
   Каждый модуль `src/` решает одну задачу и делает это хорошо.

2. **Отсутствие обратных зависимостей**
   `src/` не зависит от `apps/`, только наоборот.

3. **Полное покрытие тестами**
   Каждый атом должен иметь тесты (минимум 75% покрытия).

4. **Строгая типизация**
   Использование Pydantic и type hints для всех публичных API.

---

## См. также

- [Глобальный README](../README.md) — архитектура экосистемы
- [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md) — граница атомов и молекул
- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) — детальная архитектура

---

*Последнее обновление: 2026-07-02*
