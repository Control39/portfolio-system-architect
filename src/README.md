# src/

> **Общие библиотеки и ядро системы.** Импортируются микросервисами из `apps/`.
>
> 📋 **Архитектурное правило:** код попадает в `src/`, если используется **двумя и более** приложениями из `apps/`. Подробности в [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md).
>
> **Обновлено:** 2026-06-27 (Актуальные данные: 10 атомов)

## 📊 Статистика

| Категория | Количество |
|-----------|------------|
| **Атомов (модули)** | 10 |
| **Интеграций** | 21 сервис |
| **Тестов** | 2 |

## Назначение
- Централизованное расположение общих библиотек и утилит
- Обеспечение повторного использования кода между приложениями
- **Запрещено** импортировать код из `apps/` — `src/` должен быть независимым

## Структура — 10 атомов
- `ai/` - компоненты, связанные с искусственным интеллектом (GigaChat, Ollama bridge)
- `common/` - общие утилиты (`health_check`, `async_helpers`)
- `config/` - загрузка и валидация конфигураций
- `core/` - базовые компоненты (интерфейсы, абстракции)
- `infrastructure/` - компоненты управления инфраструктурой
- `interfaces/` - интерфейсы интеграции
- `portfolio_system_architect/` - корневой пакет
- `security/` - компоненты безопасности (маскирование секретов)
- `shared/` - общие библиотеки и схемы (LLM-клиенты и т.д.)
- `vector_store/` - ChromaDB RAG, векторные запросы

> 📦 **Архив устаревших модулей:** `decision_engine_v1/`, `repo_audit_v1/` перемещены в [`legacy/`](../legacy/). История коммитов сохранена (`git mv`).

## Ключевые импортёры (из `apps/`)

| Модуль `src/` | Используется в |
|---------------|---------------|
| `src.common.health_check` | `auth_service`, `ml-model-registry`, `job-automation-agent`, `decision-engine` |
| `src.common.async_helpers` | `ml-model-registry`, `job-automation-agent` |
| `src.embedding_agent` | `mcp-server` (опционально) |
| `src.config` | тесты, скрипты |

## ✅ Решённые проблемы

- ~~`src/decision_engine/`~~ → архивировано в `legacy/decision_engine_v1/` (см. [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md))
- ~~`src/repo_audit/`~~ → архивировано в `legacy/repo_audit_v1/` (см. [ADR-014](../architecture/decisions/ADR-014-monorepo-boundary.md))

> Активные версии: `apps/decision-engine/` и `tools/repo_audit/`.
