# Infrastructure Orchestrator

**Сервис управления развёртыванием и масштабированием микросервисов**

---

## 🎯 Назначение

Infrastructure Orchestrator предоставляет API для:
- Регистрации и управления конфигурациями сервисов
- Развёртывания и остановки экземпляров сервисов
- Масштабирования (scale up/down)
- Multi-cluster развёртывания
- Health checks и мониторинга
- Ведения истории развёртываний
- Статистики по сервисам и кластерам

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Тестов | **33** (100% проходят) |
| Покрытие | **~75%** (цель: 80%) |
| AI Config Manager | ✅ Integrated |
| Статус | 🟢 Production Ready |

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d infra-orchestrator
```

### Локальный запуск

```bash
cd apps/infra-orchestrator
python -m uvicorn main:app --reload --port 8000
```

### API Documentation

Откройте [http://localhost:8000/docs](http://localhost:8000/docs) для Swagger UI.

---

## 🔧 API Endpoints

### Health Check
- `GET /health` — Проверка здоровья сервиса
- `GET /ready` — Readiness probe
- `GET /live` — Liveness probe

### Конфигурации сервисов
- `GET /services` — Список всех конфигураций
- `POST /services` — Зарегистрировать сервис
- `GET /services/{id}` — Получить конфигурацию
- `PUT /services/{id}` — Обновить конфигурацию
- `DELETE /services/{id}` — Удалить конфигурацию

### Экземпляры сервисов
- `GET /instances` — Список экземпляров (с фильтрацией)
- `POST /instances/{service_id}/deploy` — Развернуть сервис
- `POST /instances/{id}/start` — Запустить экземпляр
- `POST /instances/{id}/stop` — Остановить экземпляр
- `DELETE /instances/{id}` — Удалить экземпляр

### Масштабирование
- `POST /instances/{id}/scale?replicas=N` — Масштабировать экземпляр

### Health checks
- `GET /instances/{id}/health` — Проверить здоровье экземпляра
- `GET /health/all` — Проверить здоровье всех экземпляров

### Статистика и история
- `GET /statistics` — Статистика по сервисам и кластерам
- `GET /history` — История развёртываний
- `GET /instances/by-type?service_type=X` — Фильтр по типу

---

## 📦 Примеры использования

### Регистрация сервиса

```bash
curl -X POST http://localhost:8000/services \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "api-001",
    "name": "Main API",
    "service_type": "api",
    "image": "myapp/api:latest",
    "replicas": 2,
    "ports": {"http": 8000},
    "environment": {"ENV": "prod"}
  }'
```

### Развёртывание

```bash
curl -X POST http://localhost:8000/instances/api-001/deploy
```

### Масштабирование

```bash
curl -X POST "http://localhost:8000/instances/api-001-20240517120000/scale?replicas=5"
```

### Проверка здоровья

```bash
curl http://localhost:8000/health/all
```

### Статистика

```bash
curl http://localhost:8000/statistics
```

---

## 🏗️ Архитектура

```
infra-orchestrator/
├── src/
│   ├── api/
│   │   ├── app.py            # FastAPI приложение
│   │   └── __init__.py
│   ├── core/
│   │   └── orchestrator.py   # Бизнес-логика (InfrastructureOrchestrator)
│   ├── config_integration.py # AI Config Manager
│   └── __init__.py
├── tests/
│   ├── test_api.py           # Тесты API (33 теста)
│   └── test_orchestrator_business.py # Бизнес-логика
├── main.py                   # Точка входа
├── Dockerfile
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/infra-orchestrator/tests/ -v

# С покрытием
pytest apps/infra-orchestrator/tests/ --cov=apps/infra_orchestrator/src --cov-report=term-missing

# Только API тесты
pytest apps/infra-orchestrator/tests/test_api.py -v
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Проверка существования сервисов перед развёртыванием
- ✅ Защита от масштабирования до 0 реплик
- ✅ Поддержка Unicode в полях

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.infra_orchestrator.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

См. [`docs/AI_CONFIG_INTEGRATION.md`](../../docs/AI_CONFIG_INTEGRATION.md) для деталей.

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8000 | `/infra-orchestrator` | 8000 |

Доступ через API Gateway: `http://localhost/infra-orchestrator/health`

---

## 📝 Известные проблемы

- Нет интеграции с Kubernetes (используется in-memory хранилище)
- Требуется добавление реального оркестратора (K8s, Docker Swarm) для production

---

*Последнее обновление: 17 мая 2026 г.*