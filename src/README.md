# src/

> **Общие библиотеки и ядро системы.** Импортируются микросервисами из `apps/`.
>
> 📋 **Архитектурное правило:** код попадает в `src/`, если используется **двумя и более** приложениями из `apps/`. Подробности в [ADR-015](../architecture/decisions/ADR-015-monorepo-boundary.md).

## Назначение
- Централизованное расположение общих библиотек и утилит
- Обеспечение повторного использования кода между приложениями
- **Запрещено** импортировать код из `apps/` — `src/` должен быть независимым

## Структура
- `ai/` - компоненты, связанные с искусственным интеллектом
- `assistant_orchestrator/` - оркестратор ИИ-ассистентов
- `common/` - общие утилиты (`health_check`, `async_helpers`)
- `config/` - загрузка и валидация конфигураций
- `core/` - базовые компоненты
- `embedding_agent/` - агент эмбеддингов для RAG
- `infrastructure/` - компоненты управления инфраструктурой
- `queues/` - управление очередями и асинхронными задачами
- `security/` - компоненты безопасности
- `shared/` - общие библиотеки и схемы (LLM-клиенты и т.д.)

> 📦 **Архив устаревших модулей:** `decision_engine_v1/`, `repo_audit_v1/` перемещены в [`legacy/`](../legacy/). История коммитов сохранена (`git mv`).

## Ключевые импортёры (из `apps/`)

| Модуль `src/` | Используется в |
|---------------|---------------|
| `src.common.health_check` | `auth_service`, `ml-model-registry`, `job-automation-agent`, `decision-engine` |
| `src.common.async_helpers` | `ml-model-registry`, `job-automation-agent` |
| `src.embedding_agent` | `mcp-server` (опционально) |
| `src.config` | тесты, скрипты |

## ✅ Решённые проблемы

- ~~`src/decision_engine/`~~ → архивировано в `legacy/decision_engine_v1/` (см. [ADR-015](../architecture/decisions/ADR-015-monorepo-boundary.md))
- ~~`src/repo_audit/`~~ → архивировано в `legacy/repo_audit_v1/` (см. [ADR-015](../architecture/decisions/ADR-015-monorepo-boundary.md))

> Активные версии: `apps/decision-engine/` и `tools/repo_audit/`.
