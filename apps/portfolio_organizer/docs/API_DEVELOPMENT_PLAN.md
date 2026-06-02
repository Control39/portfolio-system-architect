# Portfolio Organizer API - План развития

> **Дата создания:** 2026-06-02
> **Статус:** MVP + Планирование
> **Версия:** 0.1.0

---

## 📊 Текущее состояние (на 2026-06-02)

### ✅ Реализованные компоненты

| Компонент | Статус | Локация |
|-----------|--------|---------|
| **FastAPI приложение** | ✅ Готово | `src/endpoints.py` |
| **Health-check endpoints** | ✅ Готово | `src/common/health_check.py` |
| **Secret masking middleware** | ✅ Готово | `src/security/secret_masking.py` |
| **API Runner (dev/prod)** | ✅ Готово | `run_api.py` |
| **Тесты** | ✅ Частично | `tests/test_*.py` (5 файлов) |
| **Dockerfile** | ✅ Готово | `Dockerfile` |
| **README.md** | ✅ Готово | `README.md` |
| **requirements.txt** | ✅ Базовый | `requirements.txt` |

### 🔌 Существующие интеграции

```python
# ✅ Health-check (из атома src/common)
from src.common.health_check import init_health_checks

# ✅ Secret masking (из атома src/security)
from src.security.secret_masking import create_fastapi_secret_middleware
```

---

## 🎯 Основные направления доработки

### 1. Улучшение структуры и организации

**Группировка по ресурсам:**
- `/api/v1/portfolios/` — все операции с портфолио
- `/api/v1/agents/` — управление агентами
- `/api/v1/tasks/` — задачи и их статусы

**Использование APIRouter:**
```python
# apps/portfolio_organizer/api/v1/portfolios.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

class PortfolioCreate(BaseModel):
    name: str
    description: str

@router.post("/")
async def create_portfolio(portfolio: PortfolioCreate):
    # логика создания
    return {"id": 1, **portfolio.dict()}

@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    # логика получения
    return {"id": portfolio_id, "name": "Test"}
```

---

### 2. Аутентификация и авторизация

**Добавление JWT-аутентификации:**
```python
from src.security.auth import require_auth

@router.get("/protected")
@require_auth
async def protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
```

**Ролевой доступ:**
```python
@router.delete("/{portfolio_id}")
@require_auth(required_roles=["admin"])
async def delete_portfolio(portfolio_id: int):
    # только для админов
    pass
```

---

### 3. Валидация и сериализация данных

**Pydantic-модели:**
```python
class PortfolioResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    owner_id: int

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: int):
    # FastAPI автоматически валидирует ответ
    pass
```

**Валидация запросов:**
```python
class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v
```

---

### 4. Обработка ошибок

**Кастомные исключения:**
```python
from fastapi.exceptions import HTTPException

@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    portfolio = await get_portfolio_from_db(portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )
    return portfolio
```

**Глобальный обработчик:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

---

### 5. Пагинация и фильтрация

**Пагинация:**
```python
@router.get("/")
async def list_portfolios(
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "created_at",
    order: str = "desc"
):
    # логика пагинации
    return {
        "items": [...],
        "page": page,
        "total": 100
    }
```

**Фильтрация:**
```python
@router.get("/search")
async def search_portfolios(
    name_contains: Optional[str] = None,
    owner_id: Optional[int] = None,
    status: Optional[str] = None
):
    # логика поиска
    pass
```

---

### 6. Кэширование

**Кэширование ответов:**
```python
from src.common.cache import cache

@router.get("/{portfolio_id}")
@cache(ttl=300)  # кэшируем на 5 минут
async def get_portfolio(portfolio_id: int):
    # дорогая операция
    pass
```

---

### 7. Логирование и мониторинг

**Логирование запросов:**
```python
import logging

@router.post("/")
async def create_portfolio(portfolio: PortfolioCreate, request: Request):
    logger.info(
        f"Portfolio created by {request.client.host}: {portfolio.name}"
    )
    # ...
```

**Метрики Prometheus:**
```python
from prometheus_client import Counter

portfolio_created_counter = Counter(
    'portfolios_created_total',
    'Total number of portfolios created'
)

@router.post("/")
async def create_portfolio(portfolio: PortfolioCreate):
    portfolio_created_counter.inc()
    # ...
```

---

### 8. Rate limiting

**Ограничение частоты запросов:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/")
@limiter.limit("100/minute")
async def list_portfolios():
    pass
```

---

### 9. WebSockets для real-time

**Уведомления:**
```python
@router.websocket("/ws/notifications")
async def portfolio_notifications(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
```

---

### 10. Документация и примеры

**Улучшение Swagger:**
```python
@router.get(
    "/{portfolio_id}",
    response_model=PortfolioResponse,
    summary="Get portfolio by ID",
    description="Returns detailed information about a specific portfolio",
    responses={
        404: {"description": "Portfolio not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_portfolio(portfolio_id: int):
    pass
```

---

## 🚀 Дополнительные возможности

### 11. Background Tasks

**Фоновые задачи:**
```python
from fastapi import BackgroundTasks

async def send_notification(portfolio_id: int):
    # отправка email/push
    pass

@router.post("/")
async def create_portfolio(
    portfolio: PortfolioCreate,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, portfolio_id=1)
    # ...
```

---

### 12. File Upload

**Загрузка файлов:**
```python
from fastapi import UploadFile, File

@router.post("/{portfolio_id}/upload")
async def upload_portfolio_file(
    portfolio_id: int,
    file: UploadFile = File(...)
):
    contents = await file.read()
    # сохранение файла
    return {"filename": file.filename}
```

---

### 13. Versioning

**Версионирование API:**
- **URL-версионирование:** `/api/v1/`, `/api/v2/`
- **Header-версионирование:** `Accept: application/json; version=1.0`

---

### 14. HATEOAS

**Гипермедиа-ссылки:**
```python
@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    return {
        "id": portfolio_id,
        "name": "Test",
        "_links": {
            "self": f"/api/v1/portfolios/{portfolio_id}",
            "tasks": f"/api/v1/portfolios/{portfolio_id}/tasks",
            "update": f"/api/v1/portfolios/{portfolio_id}"
        }
    }
```

---

## 📋 План внедрения

### Фаза 1 (1-2 дня): Базовая структура

**Цель:** Рефакторинг структуры и базовые фичи

- [ ] **Рефакторинг структуры:** разделить на роутеры по ресурсам
  - [ ] `api/v1/portfolios.py`
  - [ ] `api/v1/agents.py`
  - [ ] `api/v1/tasks.py`
  - [ ] `api/v1/__init__.py` (объединение роутеров)

- [ ] **Добавить аутентификацию:** внедрить `require_auth` на все бизнес-эндпоинты
  - [ ] Создать `src/security/auth.py`
  - [ ] Реализовать JWT-аутентификацию
  - [ ] Добавить `get_current_user` dependency

- [ ] **Внедрить Pydantic-модели:** для запросов и ответов
  - [ ] `models/portfolio.py`
  - [ ] `models/agent.py`
  - [ ] `models/task.py`
  - [ ] `models/common.py` (общие модели)

- [ ] **Настроить логирование запросов**
  - [ ] Middleware для логирования
  - [ ] Структурированные логи (JSON)

---

### Фаза 2 (3-5 дней): Безопасность и производительность

**Цель:** Защита API и оптимизация

- [ ] **Реализация пагинации и фильтрации**
  - [ ] Универсальный механизм пагинации
  - [ ] Фильтрация по полям
  - [ ] Сортировка

- [ ] **Внедрить кэширование**
  - [ ] Создать `src/common/cache.py`
  - [ ] Интеграция с Redis (опционально)
  - [ ] Декоратор `@cache(ttl=300)`

- [ ] **Настроить rate limiting**
  - [ ] Добавить `slowapi` в requirements.txt
  - [ ] Лимиты по IP
  - [ ] Лимиты по пользователю (после auth)

- [ ] **Улучшение документации API**
  - [ ] Summary и description для всех эндпоинтов
  - [ ] Примеры ответов в Swagger
  - [ ] Коды ошибок в документации

---

### Фаза 3 (1 неделя): Продвинутые фичи

**Цель:** Расширенный функционал

- [ ] **Добавить фоновые задачи**
  - [ ] Интеграция с Celery/ARQ (опционально)
  - [ ] BackgroundTasks для email-уведомлений
  - [ ] Обработка долгих операций

- [ ] **Реализовать загрузку файлов**
  - [ ] UploadFile для изображений/документов
  - [ ] Валидация типов файлов
  - [ ] Хранение (локально/S3)

- [ ] **Внедрить HATEOAS**
  - [ ] Добавление `_links` в ответы
  - [ ] Навигация по ресурсам

- [ ] **Настроить метрики Prometheus**
  - [ ] Добавить `prometheus_client` в requirements.txt
  - [ ] Counter для ключевых операций
  - [ ] Histogram для latency

---

### Фаза 4 (2 недели): Real-time и надёжность

**Цель:** Полноценное production-приложение

- [ ] **Внедрить WebSocket**
  - [ ] Real-time уведомления
  - [ ] Live-статус задач
  - [ ] Multi-user синхронизация

- [ ] **Глобальный обработчик ошибок**
  - [ ] Кастомные исключения (PortfolioNotFound, etc.)
  - [ ] Единый формат ошибок
  - [ ] Логирование с контекстом

- [ ] **Комплексное тестирование**
  - [ ] Integration tests для всех роутеров
  - [ ] E2E тесты с TestClient
  - [ ] Тесты аутентификации

- [ ] **Документирование**
  - [ ] API Reference в отдельном Markdown
  - [ ] Примеры использования
  - [ ] Troubleshooting guide

---

## 📦 Зависимости для установки

### Фаза 1 (Базовая):
```txt
# Уже есть
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
httpx>=0.24.0
```

### Фаза 2 (Безопасность):
```txt
# Добавить
python-jose[cryptography]>=3.3.0  # JWT
passlib[bcrypt]>=1.7.4  # хеширование паролей
slowapi>=0.1.9  # rate limiting
redis>=4.5.0  # кэширование (опционально)
```

### Фаза 3 (Продвинутая):
```txt
# Добавить
celery>=5.3.0  # фоновые задачи (опционально)
prometheus-client>=0.17.0  # метрики
python-multipart>=0.0.6  # file upload
boto3>=1.28.0  # S3 storage (опционально)
```

### Фаза 4 (Production):
```txt
# Добавить
websockets>=11.0  # WebSocket support
aioredis>=2.0.0  # async Redis
```

---

## 🎯 Приоритеты

| Приоритет | Фича | Фаза | Почему важно |
|-----------|------|------|--------------|
| 🔥 **P0** | APIRouter структура | 1 | Основа для масштабирования |
| 🔥 **P0** | Pydantic модели | 1 | Валидация данных |
| 🔥 **P0** | JWT аутентификация | 2 | Безопасность |
| ⚡ **P1** | Пагинация | 2 | Производительность |
| ⚡ **P1** | Rate limiting | 2 | Защита от перегрузки |
| ⚡ **P1** | Кэширование | 2 | Скорость ответов |
| ⚪ **P2** | Background tasks | 3 | Асинхронность |
| ⚪ **P2** | Prometheus | 3 | Мониторинг |
| ⚪ **P2** | File upload | 3 | Функциональность |
| ⚪ **P3** | WebSocket | 4 | Real-time |
| ⚪ **P3** | HATEOAS | 4 | REST compliance |

---

## 📝 Примечания

### Существующие атомы (переиспользуемые компоненты):

```
src/
├── common/
│   ├── health_check.py  ✅ Используется
│   └── async_helpers.py
├── security/
│   ├── secret_masking.py  ✅ Используется
│   └── auth.py  ❌ Нужно создать
└── shared/
    └── ...
```

### Известные ограничения:

1. **Нет базы данных** — пока нет реализации CRUD операций
2. **Нет Redis** — кэширование не реализовано
3. **Нет Celery/ARQ** — фоновые задачи через FastAPI BackgroundTasks
4. **JWT не реализован** — нужна `src/security/auth.py`

---

## 🔄 История изменений

| Дата | Изменения | Автор |
|------|-----------|-------|
| 2026-06-02 | Создан документ с планом развития | @Control39 |

---

**Связанные документы:**
- [README.md](../README.md) — общая документация
- [API_REFERENCE.md](./API_REFERENCE.md) — детальное описание API (в планах)
- [DEPLOYMENT.md](./DEPLOYMENT.md) — инструкции по развёртыванию

---

*Последнее обновление: 2026-06-02*
