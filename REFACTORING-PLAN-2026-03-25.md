# План Рефакторинга: Health-Check & Async Code
**Дата**: 25 марта 2026  
**Автор**: GitHub Copilot  
**Статус**: В процессе

---

## 📋 Обзор Проблем

### 1. Дублирование Health-Check Эндпоинтов (Приоритет: ВЫСОКИЙ)

#### Найдено 5+ мест с реализацией:
- ✗ `auth-service/main.py` — `/health`
- ✗ `cloud-reason/api/reasoning_api.py`
- ✗ `cloud-reason/api/endpoints.py` — `async def health()`
- ✗ `ml-model-registry/src/api/portfolio_integration.py` — `/health`
- ✗ `portfolio-organizer/src/app.py` — `/health`
- ✗ `portfolio-organizer/src/api/reasoning_api.py` — `/health`
- ✗ `portfolio-organizer/src/api/ml_model_registry_integration.py` — `/health`
- ✗ `scripts/healthcheck.py` — отдельный скрипт

**Проблемы:**
- Несогласованные форматы ответа
- Разные порты и пути
- Отсутствует единая логика проверки статуса
- Сложность тестирования

---

### 2. Асинхронный Код с Глубокой Вложенностью (Приоритет: СРЕДНИЙ)

#### Идентифицированные проблемы:

**a) ml-model-registry** — Sequential async calls в `export_model_to_portfolio()`:
```python
model_data = await fetch_from_registry(...)      # 1
export_data = await fetch_from_registry(...)     # 2
portfolio_response = await send_to_portfolio(...) # 3
```
→ Можно распараллелить шаги 1 и 2

**b) job-automation-agent** — Множественные async функции:
- `search_hh_ru()` — сетевой запрос
- `generate_resume()` — обработка
- `run_core_agent()` — оркестрация
→ Нет управления ошибками и таймаутами

**c) career-development** — DB операции в цикле:
```python
for skill in profile.get("skills", []):
    for marker in skill.get("markers", []):
        # Каждый раз файл I/O
```
→ Можно использовать batch операции

---

## 🎯 Стратегия Рефакторинга

### Этап 1: Создание Общего Health-Check Модуля
**Файл**: `src/common/health_check.py`

```python
# Структура
class HealthCheckService:
    - check_db_connection()
    - check_external_service()
    - get_service_health()
    
@router.get("/health")
@router.get("/ready") 
@router.get("/live")
```

**Преимущества:**
- Единая точка контроля
- Стандартный формат ответа
- Легко расширяемо

---

### Этап 2: Оптимизация Асинхронного Кода
**Файл**: `src/common/async_helpers.py`

```python
# Функции:
async def fetch_parallel(*tasks)        # asyncio.gather()
async def fetch_with_timeout()          # Управление таймаутами
async def fetch_with_retry()            # Exponential backoff
async def batch_async_operations()      # Batch processing
```

---

### Этап 3: Примеры Рефакторинга

#### 3.1 Минимальный дублирование Health-Check
```diff
# ДО:
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth-service"}

# ПОСЛЕ:
from src.common.health_check import init_health_checks
init_health_checks(app, "auth-service", db=None)
```

#### 3.2 Параллельные Async Запросы
```diff
# ДО: Sequential (~30 сек на 3 запроса)
model_data = await fetch_from_registry(...)
export_data = await fetch_from_registry(...)
portfolio_response = await send_to_portfolio(...)

# ПОСЛЕ: Parallel (~15 сек)
model_data, export_data = await fetch_parallel(
    fetch_from_registry(...),
    fetch_from_registry(...)
)
portfolio_response = await send_to_portfolio(...)
```

---

## 📊 График Рефакторинга

| Этап | Компонент | Сложность | Время | Зависимости |
|------|-----------|-----------|-------|------------|
| 1 | `src/common/health_check.py` | Низкая | 1-2 часа | — |
| 1 | `src/common/async_helpers.py` | Средняя | 2-3 часа | — |
| 2 | auth-service | Низкая | 30 мин | Этап 1 |
| 2 | cloud-reason | Низкая | 30 мин | Этап 1 |
| 2 | portfolio-organizer | Средняя | 1 час | Этап 1 |
| 3 | ml-model-registry | Средняя | 2 часа | Этап 1, 2 |
| 3 | career-development | Средняя | 1.5 часа | Этап 1, 2 |
| 4 | job-automation-agent | Средняя | 1.5 часа | Этап 1, 2 |
| 5 | Тестирование | Средняя | 2 часа | Все выше |
| 6 | Слияние в main | Низкая | 30 мин | Все выше |

**Итого**: ~13-14 часов

---

## 🔍 Веточная Стратегия

### Текущее Состояние:
```
origin (GitHub)
├── main (текущая)
├── blackboxai/job-automation-system
├── blackboxai/tree-v2
├── reorg-10-directions-2026-03-21
└── fix-deploy-errors

upstream (SourceCraft)
└── (проверить синхронизацию)
```

### Веточная Стратегия:
```
main
└── refactor/health-check-consolidation (1-2 часа)
    ├── feat/common-health-check-module (Этап 1)
    ├── feat/async-helpers-module (Этап 1)
    ├── refactor/auth-service-health (Этап 2)
    ├── refactor/cloud-reason-health (Этап 2)
    ├── refactor/portfolio-organizer (Этап 3)
    ├── refactor/ml-model-registry (Этап 3)
    └── refactor/career-development-async (Этап 3)

└── refactor/job-automation-agent (Этап 4)
    └── refactor/async-orchestration

Все ветки → PR → Code Review → Merge в refactor/health-check-consolidation
→ Final PR → main
```

---

## ✅ Чек-Лист Выполнения

### фаза 1: Подготовка
- [ ] Создать feature branch `refactor/health-check-consolidation`
- [ ] Создать `src/common/` директорию
- [ ] Написать unit тесты для новых модулей

### Фаза 2: Health-Check Модуль
- [ ] Реализовать `src/common/health_check.py`
- [ ] Добавить поддержку `/health`, `/ready`, `/live`
- [ ] Написать тесты
- [ ] Обновить auth-service
- [ ] Обновить cloud-reason
- [ ] Обновить portfolio-organizer
- [ ] Обновить ml-model-registry
- [ ] Обновить другие сервисы
- [ ] Удалить scripts/healthcheck.py или переиспользовать

### Фаза 3: Async Helpers
- [ ] Реализовать `src/common/async_helpers.py`
- [ ] Написать тесты
- [ ] Обновить ml-model-registry
- [ ] Обновить job-automation-agent
- [ ] Обновить career-development

### Фаза 4: Тестирование
- [ ] Запустить unit тесты
- [ ] Запустить e2e тесты
- [ ] Проверить совместимость с K8s
- [ ] Проверить Docker развертывание

### Фаза 5: Мержинг
- [ ] Создать final PR
- [ ] Code review
- [ ] Merge в main
- [ ] Удалить feature branches
- [ ] Обновить documentation

---

## 📝 Примеры Кода

### common/health_check.py
```python
"""Единый модуль для health-check эндпоинтов."""
from fastapi import APIRouter, HTTPException
from typing import Callable, Optional
import asyncio

class HealthCheckService:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.checks = {}
    
    def register_check(self, name: str, check_fn: Callable):
        """Регистрирует функцию проверки."""
        self.checks[name] = check_fn
    
    async def get_health(self):
        """Получить полный статус здоровья сервиса."""
        results = {}
        for name, check_fn in self.checks.items():
            try:
                results[name] = await asyncio.wait_for(
                    check_fn(), timeout=5
                )
            except asyncio.TimeoutError:
                results[name] = {"status": "timeout"}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        
        status = "healthy" if all(
            r.get("status") == "ok" for r in results.values()
        ) else "degraded"
        
        return {
            "service": self.service_name,
            "status": status,
            "checks": results
        }

def init_health_checks(app, service_name: str, db=None):
    """Инициализировать health-check endpoints."""
    router = APIRouter()
    service = HealthCheckService(service_name)
    
    if db:
        async def check_db():
            try:
                await db.ping()
                return {"status": "ok"}
            except:
                return {"status": "error"}
        service.register_check("database", check_db)
    
    @router.get("/health")
    @router.get("/ready")
    @router.get("/live")
    async def health():
        return await service.get_health()
    
    app.include_router(router)
```

---

## 🚀 Команды для Выполнения

```bash
# 1. Создать feature branch
git checkout -b refactor/health-check-consolidation

# 2. Создать общие модули
mkdir -p src/common
touch src/common/__init__.py
touch src/common/health_check.py
touch src/common/async_helpers.py

# 3. Запустить тесты
python -m pytest tests/ -v

# 4. Проверить конфликты
git diff main..HEAD

# 5. Создать PR
# (через GitHub UI)
```

---

## 💡 Best Practices

1. **Health-Check Format**: JSON с полями `service`, `status`, `checks`
2. **Timeout Management**: Всегда устанавливать таймауты для async операций
3. **Error Handling**: Retry логика с exponential backoff
4. **Parallel Operations**: Использовать `asyncio.gather()` где возможно
5. **Testing**: Unit тесты для каждого модуля перед интеграцией

---

## 📚 Документация

- [FastAPI Health Checks](https://fastapi.tiangolo.com)
- [Python asyncio Best Practices](https://docs.python.org/3/library/asyncio.html)
- [Kubernetes Probes Configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

