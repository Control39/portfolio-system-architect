# ADR-015: Граница между `src/` и `apps/` в монорепозитории

## Статус

Принято

## Контекст

В репозитории `portfolio-system-architect` сосуществуют две корневые папки с кодом:
- `src/` — общие библиотеки, ядро, утилиты
- `apps/` — самостоятельные микросервисы и приложения

Необходимо чётко зафиксировать архитектурное правило: что класть в `src/`, что в `apps/`, и почему.

## Решение

### Правило разделения

| Папка | Что здесь | Критерий принадлежности |
|-------|-----------|------------------------|
| **`src/`** | Общие библиотеки, ядро, shared-компоненты | Код, который импортируется **двумя и более** приложениями из `apps/` |
| **`apps/`** | Самостоятельные микросервисы и приложения | Код, который имеет свою точку входа (`main.py`), Dockerfile, и может быть развёрнут независимо |

### Примеры из проекта

**`src/` — общие компоненты:**
- `src.common.health_check` — health check используется в `auth_service`, `ml-model-registry`, `job-automation-agent`, `decision-engine`
- `src.common.async_helpers` — async утилиты для `ml-model-registry`, `job-automation-agent`
- `src.embedding_agent` — RAG/эмбеддинги для `mcp-server` (опционально) и тестов
- `src.config` — загрузка конфигураций для всей экосистемы
- `src.security` — общие компоненты безопасности

**`apps/` — независимые сервисы:**
- `apps/auth_service/` — JWT аутентификация, свой Dockerfile, порт 8100
- `apps/decision-engine/` — RAG API, своё ядро reasoning, порт 8001
- `apps/it_compass/` — Streamlit UI, порт 8501
- `apps/ml-model-registry/` — реестр ML-моделей, порт 8001

### Направление зависимостей

```
apps/*/ → src/*          (apps импортируют общие библиотеки)
src/*   ↛ apps/*         (src НЕ зависит от apps — запрещено)
apps/*  ↛ apps/*/        (apps могут взаимодействовать через API, не импорты)
```

### Внутренняя структура `apps/*`

Каждое приложение в `apps/` МОЖЕТ иметь **собственный** `src/` внутри себя:
```
apps/template-service/
├── src/              ← внутренний src сервиса (не путать с корневым src/)
│   ├── api/
│   └── core/
├── Dockerfile
└── requirements.txt
```

Импорты вида `from src.api import router` внутри `apps/template-service/src/main.py` относятся к **внутреннему** `src` сервиса, а не к корневому `src/`.

## Последствия

- ✅ **DRY** — общая логика в одном месте (`src/`)
- ✅ **Независимость деплоя** — каждый сервис из `apps/` можно билдить и деплоить отдельно
- ✅ **Тестируемость** — `src/` тестируется через `tests/unit/`, `apps/` — через собственные тесты + интеграционные
- ⚠️ **Риск дублирования** — если общий код остаётся только в одном apps, его нужно вынести в `src/`

## Решённые нарушения (архивированы)

> ✅ Устаревшие версии перемещены в `legacy/` для сохранения истории коммитов и контекста.

| Нарушение | Было | Стало | Решение |
|-----------|------|-------|---------|
| Дублирование `decision_engine` | `src/decision_engine/` + `apps/decision-engine/` | `apps/decision-engine/` — активный сервис; `legacy/decision_engine_v1/` — архив | Анализ импортов показал: `src/decision_engine/` не импортировался никем из `apps/`, тестировался только `tests/unit/test_decision_engine_init.py`. Перемещён в `legacy/decision_engine_v1/` через `git mv`. |
| Дублирование `repo_audit` | `src/repo_audit/` + `tools/repo_audit/` | `tools/repo_audit/` — активный инструмент (CI/CD `repo-audit.yml`); `legacy/repo_audit_v1/` — архив | Анализ импортов показал: `src/repo_audit/` имел **0 импортёров**, `tools/repo_audit/` используется в CI/CD, `pyproject.toml`, документации. Перемещён в `legacy/repo_audit_v1/` через `git mv`. |

### Проверка после рефакторинга

- [x] `src/__init__.py` очищен от `decision_engine` и `repo_audit`
- [x] `tests/unit/test_decision_engine_init.py` перемещён в `legacy/test_decision_engine_init_v1.py`
- [x] Нет битых импортов: `grep -r "from src.decision_engine"` и `grep -r "from src.repo_audit"` возвращают 0 результатов

## Связанные решения

- [ADR-009: Базовые Docker-образы](ADR-009-base-docker-images.md) — `docker/base-images/` используются apps/
- [ADR-002: Компонентная интеграция](ADR-002-component-integration.md) — принципы взаимодействия компонентов

## Владелец решения

Екатерина Куделя — Cognitive Systems Architect
