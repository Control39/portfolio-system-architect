# System Proof

**Сервис валидации критериев производственной готовности**

---

## 🎯 Назначение

System Proof предоставляет API для:
- Создания и управления доказательствами производственной готовности
- Верификации шагов доказательств
- Фильтрации и поиска по доказательствам
- Генциации статистики по статусам

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Тестов | **19** (100% проходят) |
| Покрытие | **~75%** (цель: 80%) |
| AI Config Manager | ✅ Integrated |
| Статус | 🟢 Production Ready |

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d system-proof
```

### Локальный запуск

```bash
cd apps/system_proof
python -m uvicorn src.app:app --reload --port 8003
```

### API Documentation

Откройте [http://localhost:8003/docs](http://localhost:8003/docs) для Swagger UI.

---

## 🔧 API Endpoints

### Health Check
- `GET /health` — Проверка здоровья сервиса
- `GET /ready` — Readiness probe
- `GET /live` — Liveness probe

### Доказательства
- `GET /proofs` — Список всех доказательств
- `POST /proofs` — Создать новое доказательство
- `GET /proofs/{id}` — Получить доказательство по ID
- `PUT /proofs/{id}` — Обновить доказательство
- `DELETE /proofs/{id}` — Удалить доказательство

### Шаги доказательств
- `POST /proofs/{id}/steps` — Добавить шаг к доказательству
- `POST /proofs/{id}/verify` — Верифицировать все шаги

### Фильтрация
- `GET /proofs?architecture=microservices` — Фильтр по архитектуре
- `GET /proofs?status=verified` — Фильтр по статусу

### Статистика
- `GET /statistics` — Статистика по доказательствам

---

## 📦 Примеры использования

### Создание доказательства

```bash
curl -X POST http://localhost:8003/proofs \
  -H "Content-Type: application/json" \
  -d '{
    "proof_id": "proof-001",
    "architecture": "microservices",
    "chain_id": "chain-001",
    "title": "Production Readiness Proof",
    "description": "Доказательство готовности к production",
    "steps": []
  }'
```

### Добавление шага

```bash
curl -X POST http://localhost:8003/proofs/proof-001/steps \
  -H "Content-Type: application/json" \
  -d '{
    "step_id": "step-001",
    "description": "Настроено мониторинг",
    "evidence": "Grafana дашборд создан"
  }'
```

### Верификация

```bash
curl -X POST http://localhost:8003/proofs/proof-001/verify
```

---

## 🏗️ Архитектура

```
system_proof/
├── src/
│   ├── app.py              # FastAPI приложение
│   ├── config_integration.py # AI Config Manager
│   ├── core.py             # Бизнес-логика (ProofCollection)
│   └── __init__.py
├── tests/
│   ├── test_api.py         # Тесты API (19 тестов)
│   ├── test_proof_basic.py # Базовые тесты
│   └── test_proof_business.py # Бизнес-логика
├── Dockerfile
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/system_proof/tests/ -v

# С покрытием
pytest apps/system_proof/tests/ --cov=apps/system_proof/src --cov-report=term-missing

# Только API тесты
pytest apps/system_proof/tests/test_api.py -v
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Проверка существования ресурсов
- ✅ Защита от дубликатов ID
- ✅ Поддержка Unicode в полях

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.system_proof.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

См. [`docs/AI_CONFIG_INTEGRATION.md`](../../docs/AI_CONFIG_INTEGRATION.md) для деталей.

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8003 | `/system-proof` | 8003 |

Доступ через API Gateway: `http://localhost/system-proof/health`

---

## 📝 Известные проблемы

- Нет интеграции с PostgreSQL (используется in-memory хранилище)
- Требуется добавление persistence слоя

---

*Последнее обновление: 17 мая 2026 г.*