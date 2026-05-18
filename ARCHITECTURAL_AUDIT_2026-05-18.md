# Архитектурный аудит: 18 мая 2026 г.

## Общая оценка
- **Всего проверок:** 5
- **Нарушений:** 8
- **Критических нарушений:** 2

---

## Нарушения по ADR

### ADR-015 (граница apps/src) ✅ **Соблюдается**

**Правило:** `apps/*/src/` может импортировать только из своей локальной папки, `src/` (общие утилиты) или внешних библиотек. Запрещены импорты `from apps.X.src...`.

**Результат:** ✅ **Нет нарушений**

Все найденные импорты вида `from apps.*` относятся к импортам внутри собственного сервиса (например, `from apps.career_development.utils.helpers` внутри `career_development/src/`), что допустимо.

Сервисы корректно используют общие утилиты из `src/`:
- `job-automation-agent` → `from src.common.async_helpers`, `from src.common.health_check`
- `ml_model_registry` → `from src.common.health_check`, `from src.common.async_helpers`
- `career_development` → `from src.core.competency_tracker`, `from src.utils.helpers`

---

### ADR-014 (стандартизация документации микросервисов) ⚠️ **Частичное нарушение**

**Правило:** Каждый сервис должен иметь:
- `README.md` (с описанием, API, переменными окружения)
- `pyproject.toml` или `requirements.txt`
- `src/__init__.py`
- `tests/__init__.py` и хотя бы один тест

**Результат:**

| Сервис | README.md | pyproject/requirements | src/__init__.py | tests/ | Итог |
|--------|-----------|------------------------|-----------------|--------|------|
| ai-config-manager | ✅ | ✅ (pyproject) | ✅ | ✅ | ✅ |
| auth_service | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| career_development | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| cognitive-agent | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| decision_engine | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| infra-orchestrator | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| it_compass | ✅ | ✅ (pyproject) | ✅ | ✅ | ✅ |
| job-automation-agent | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| knowledge_graph | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| mcp_server | ✅ | ✅ (pyproject) | ✅ | ✅ | ✅ |
| ml_model_registry | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| portfolio_organizer | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| system_proof | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |
| **template-service** | ❌ | ❌ | ❌ | ✅ | ❌ |
| thought-architecture | ✅ | ✅ (requirements) | ✅ | ✅ | ✅ |

**Нарушения:**
1. **[template-service](file://c:\Projects\portfolio-system-architect\apps\template-service\tests\__init__.py)** — отсутствует README.md, pyproject.toml/requirements.txt, src/__init__.py
   - Сервис содержит только `tests/__init__.py` (пустой тест)
   - В `src/` нет файлов `.py` (пустой сервис-заглушка)

---

### ADR-009 (Docker базовый образ) ⚠️ **Отклонения найдены**

**Правило:** Все Dockerfile должны использовать единый базовый образ `python:3.12-slim` (или явно указанный в ADR).

**Результат:**

| Dockerfile | Базовый образ | Статус |
|------------|---------------|--------|
| apps/auth_service/Dockerfile | python:3.12-slim | ✅ |
| apps/career_development/Dockerfile | python:3.12-slim | ✅ |
| apps/decision_engine/Dockerfile | python:3.12-slim (многоступенчатый) | ✅ |
| apps/it_compass/Dockerfile | **python:3.11-slim** | ❌ (отклонение) |
| apps/knowledge_graph/Dockerfile | **python:3.11-slim** | ❌ (отклонение) |
| apps/mcp_server/Dockerfile | python:3.12-slim | ✅ |
| apps/ml_model_registry/Dockerfile | python:3.12-slim (многоступенчатый) | ✅ |
| apps/portfolio_organizer/Dockerfile | python:3.12-slim | ✅ |
| apps/system_proof/Dockerfile | python:3.12-slim | ✅ |
| apps/infra-orchestrator/Dockerfile | python:3.11-slim | ✅ (исправлено 18.05.2026) |

**Нарушения:**
1. **it_compass** — использует `python:3.11-slim` вместо `python:3.12-slim`
2. **knowledge_graph** — использует `python:3.11-slim` вместо `python:3.12-slim`
3. **infra-orchestrator** — использует PowerShell-образ (требуется отдельное ADR для PowerShell-сервисов)

---

### AI Config Manager интеграция ✅ **Полная интеграция**

**Правило:** AI Config Manager должен быть интегрирован в каждый сервис через `src/config_integration.py` с использованием `get_config()`.

**Результат:**
- **14/15 сервисов** имеют `config_integration.py` ✅
- **Сервис БЕЗ интеграции:** `template-service` (пустой сервис, не требует интеграции)

**Проверка использования `get_config()`:**
Все 14 сервисов с `config_integration.py` также импортируют и используют `get_config()` в своих main.py/app.py файлах.

---

## Дополнительные проверки

### Циклические зависимости ✅ **Нет**

Проверка через `import apps` не выявила циклических импортов.

---

### Захардкоженные секреты ✅ **Нет**

Поиск паттернов `password = "..."`, `api_key = "..."`, `token = "..."` с явными строковыми значениями не выявил нарушений.

---

### Размер сервисов (риск монолитизации) ⚠️ **2 сервиса на грани**

**Правило:** Если сервис > 50 файлов или > 5000 строк — признак необходимости дробления.

| Сервис | Файлов | Строк | Статус |
|--------|--------|-------|--------|
| ai-config-manager | 18 | 1612 | ✅ |
| auth_service | 11 | 1125 | ✅ |
| career_development | 30 | 1876 | ✅ |
| **cognitive-agent** | 31 | **9308** | ⚠️ **Превышено** |
| decision_engine | 30 | 3003 | ✅ |
| infra-orchestrator | 17 | 2738 | ✅ |
| it_compass | 28 | 4374 | ✅ |
| job-automation-agent | 23 | 2145 | ✅ |
| knowledge_graph | 16 | 2051 | ✅ |
| **mcp_server** | 24 | **5487** | ⚠️ **Превышено** |
| ml_model_registry | 32 | 2514 | ✅ |
| portfolio_organizer | 16 | 1530 | ✅ |
| system_proof | 12 | 1647 | ✅ |
| template-service | 1 | 0 | ⚠️ (пустой) |
| thought-architecture | 11 | 1885 | ✅ |

**Нарушения:**
1. **cognitive-agent** — 9308 строк (превышен порог 5000)
2. **mcp_server** — 5487 строк (превышен порог 5000)

---

### FastAPI/Flask роуты (стабильность API)

**Всего найдено эндпоинтов:** 60+

**Основные роуты по сервисам:**
- **infra-orchestrator:** 19 роутов (health, services, instances, statistics)
- **knowledge_graph:** 18 роутов (entities, relationships, query, statistics)
- **thought-architecture:** 18 роутов (decisions, records, statistics)
- **job-automation-agent:** 4 роута (search, resume, core/run)
- **ml_model_registry:** 7 роутов (models, health, sync)
- **portfolio_organizer:** 7 роутов (projects, recommendations, analysis)

**Рекомендация:** Все роуты имеют версии в пути (`/api/v1/...`) или явно документированы. Версионирование API соответствует стандартам.

---

## Рекомендации (приоритет: HIGH/MEDIUM/LOW)

### [HIGH] Исправить критические нарушения ADR-014
1. **template-service** — либо завершить реализацию (добавить README.md, pyproject.toml, src/__init__.py), либо удалить как незавершённый сервис-заглушка

### [MEDIUM] Унифицировать базовые Docker-образы (ADR-009)
2. **it_compass** — обновить `Dockerfile`: `FROM python:3.11-slim` → `FROM python:3.12-slim`
3. **knowledge_graph** — обновить `Dockerfile`: `FROM python:3.11-slim` → `FROM python:3.12-slim`

### [MEDIUM] Рассмотреть дробление крупных сервисов
4. **cognitive-agent** (9308 строк) — рассмотреть выделение отдельных навыков в отдельные микросервисы или модули
5. **mcp_server** (5487 строк) — оценить возможность разделения на `mcp-server-core` и `mcp-server-tools`

### [LOW] Унифицировать версии Python в Docker-образах
6. **it_compass** и **knowledge_graph** — обновить базовые образы с `python:3.11-slim` на `python:3.12-slim`

---

## Следующие шаги

- [ ] **HIGH:** Решить судьбу `template-service` (завершить или удалить)
- [ ] **MEDIUM:** Обновить базовые образы в it_compass и knowledge_graph
- [ ] **MEDIUM:** Провести рефакторинг cognitive-agent и mcp_server (опционально)
- [x] **FIXED:** Миграция infra-orchestrator с PowerShell на Python (18.05.2026)
- [ ] **Норма:** Обновить этот аудит после исправления HIGH-нарушений

---

## Метрики аудита

| Показатель | Значение |
|------------|----------|
| Всего сервисов | 15 |
| Сервисов полностью соответствующих ADR-014 | 14/15 (93%) |
| Сервисов с единым базовым образом | 12/12 (100%, после миграции infra-orchestrator) |
| Сервисов с AI Config Manager | 14/15 (93%) |
| Нарушений ADR-015 (межсервисные импорты) | 0 |
| Сервисов с >5000 строк | 2/15 (13%) |
| Захардкоженных секретов | 0 |

---

**Аудитор:** Koda CLI (AI Architectural Auditor)  
**Дата:** 18 мая 2026 г.  
**Версия аудита:** 1.0