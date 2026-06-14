# ADR-023: Переход на событийную архитектуру (с сохранением AI Config Manager)

**Дата:** 2026-05-20 (обновлено: 2026-06-13) **Статус:** 🟢 Принято к реализации **Автор:** Kudelya
Ekaterina **Контекст:** \[См. полное описание в README проекта\]

______________________________________________________________________

## 🔍 Проблема

Текущая реализация — **distributed monolith**:

- 26+ прямых импортов сервисов друг из друга (особенно `ai_config_manager` → 15 микросервисов)
- Микросервисы не изолированы (нельзя масштабировать, отлаживать)
- HTTP-вызовов между сервисами — **0**, но есть критические импортные зависимости

> Пример нарушения: `apps/portfolio_organizer/src/core/validator.py` →
> `from ai_config_manager.config_manager import ConfigManager`
> `apps/system_proof/src/core/reasoning.py` →
> `from cognitive_agent.orchestrator import Orchestrator`

______________________________________________________________________

## ⚠️ **ВАЖНОЕ УТОЧНЕНИЕ: AI Config Manager — это НЕ просто библиотека**

**Ошибка в первоначальном анализе:** Предлагалось упразднить `ai_config_manager` как сервис.

**Факты (из README и кода):**

| Факт | Доказательство | |------|----------------| | **HTTP API** | Порт 8000,
`/api/v1/config/{service}`, Swagger UI, 7 endpoints | | **71 тест** | 100% пройдено (45 unit + 20
integration + 6 E2E) | | **15 сервисов** | Все используют `/api/v1/config` для получения конфигов |
| **Hot reload** | Сервис перечитывает YAML без рестарта | | **Метрики** | Prometheus
(config_loads_total, config_reloads_total, config_load_duration_seconds) | | **Маскирование** |
`security.py` — скрывает секреты в логах |

**Вывод:** Упразднение сервиса = убийство централизованного управления конфигурациями, hot reload и
HTTP API.

______________________________________________________________________

## ✅ Решение

Перейти к **event-driven архитектуре** с:

1. **AI Config Manager — сохраняется как сервис** (порт 8000)
1. **Redis Streams** как event bus (упрощённый Kafka, без сложной инфраструктуры)
1. **Outbox pattern** для надёжной доставки событий
1. **CQRS**: REST-команды (POST/PUT) + асинхронные события
1. **Изоляция сервисов**: ни один `apps/` не импортирует другой (кроме ConfigManager как библиотеки)

______________________________________________________________________

## 🧱 Ключевые изменения

### 1. **AI Config Manager — критический компонент (не упраздняем!)**

**Архитектура:**

```
AI Config Manager (микросервис, порт 8000)
├── FastAPI API: /api/v1/config/{service}
├── ConfigManager (внутренняя библиотека)
├── YAML конфиг (единый источник истины)
└── Prometheus метрики
```

**Использование другими сервисами:**

```python
# ❌ ПЛОХО: прямой импорт
from apps.ai_config_manager.src.config_manager import ConfigManager

# ✅ ХОРОШО: HTTP API + fallback
import httpx

class ConfigClient:
    def __init__(self, service_name: str):
        self.api_url = "http://ai_config_manager:8000"
        self.service_name = service_name
        self.local_config_path = Path(f"config/{service_name}.yaml")

    async def get_config(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(f"{self.api_url}/api/v1/config/{self.service_name}")
                resp.raise_for_status()
                config = resp.json()
                # Сохранить в локальный кэш
                self.local_config_path.write_text(str(config))
                return config
        except httpx.RequestError:
            # Fallback: читать из локального кэша
            if self.local_config_path.exists():
                return yaml.safe_load(self.local_config_path.read_text())
            raise RuntimeError("Нет конфига ни в API, ни в кэше")
```

### 2. **Event Bus (Redis Streams)**

- Добавить `redis/redis-stack` в `docker-compose.yml`
- Каждый сервис пишет события в таблицу `outbox_events` (PostgreSQL)
- Воркер `outbox_publisher` публикует в Redis Streams

### 3. **Первые 2 события (приоритет)**

| Событие | Публикатор | Слушатель | Цель | |---------|------------|-----------|------| |
`portfolio.events.project.created` | Portfolio Organizer | System Proof | Валидация маршрута при
создании проекта | | `proof.events.route.validated` | System Proof | Career Development | Обновление
карьерного плана после валидации |

### 4. **Outbox pattern (в каждом сервисе)**

```python
# apps/portfolio_organizer/outbox.py
def record_event(event_type: str, payload: dict):
    db.insert("outbox_events", {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "payload": json.dumps(payload),
        "created_at": datetime.utcnow(),
        "published": False
    })
```

______________________________________________________________________

## 🛡️ Устойчивость AI Config Manager (устранение SPOF)

### Проблема: Single Point of Failure

Если `ai_config_manager` падает → все 15 сервисов теряют конфигурацию.

### Решение: Fallback mechanism

**Шаг 1: Локальный кэш в каждом сервисе**

```yaml
# docker-compose.yml
services:
  decision_engine:
    volumes:
      - ./config:/app/config  # Копия конфигов локально
    environment:
      - CONFIG_SERVICE_URL=http://ai_config_manager:8000
      - CONFIG_FALLBACK_ENABLED=true
```

**Шаг 2: Health check + degraded mode**

```python
# apps/decision_engine/src/config_integration.py
def is_config_service_healthy() -> bool:
    try:
        resp = httpx.get("http://ai_config_manager:8000/health", timeout=1.0)
        return resp.status_code == 200
    except:
        return False

def get_config():
    if is_config_service_healthy():
        # Получать из API
        return fetch_from_api()
    else:
        # Fallback: локальный кэш
        logger.warning("AI Config Manager недоступен, использую локальный кэш")
        return load_from_local_cache()
```

**Шаг 3: Автоматическое восстановление**

```python
# При восстановлении сервиса:
if is_config_service_healthy():
    refresh_local_cache()  # Синхронизировать с API
```

______________________________________________________________________

## 📊 Метрики успеха

| Показатель | Текущее | Цель | Статус | |------------|---------|------|--------| | **Тестов** | 71
| 71 | ✅ | | **Сервисов** | 15 | 15 | ✅ | | **Uptime** | 99.9% | 99.95% | 🟡 (нужен fallback) | |
**Latency** | 50 ms | \<20 ms | 🟡 (кэшировать) | | **Импортов apps/ → apps/** | 26+ | 0 | 🟡
(планируется) |

______________________________________________________________________

## 🚀 План реализации (Фаза 1: 5 дней)

| День | Задача | Критерий успеха | |------|--------|-----------------| | **1–2** | Оставить
ai_config_manager как сервис, добавить fallback | 0 падений при отключении API | | **3** | Поднять
redis-stack в docker-compose.yml | `redis-cli PING` → PONG | | **4** | Реализовать событие
`project.created` | Через `/api/v1/projects` создаёшь проект → в Redis появляется событие | | **5**
| Реализовать слушатель `route.validated` в System Proof | Событие `project.created` → System Proof
валидирует → публикует `route.validated` |

______________________________________________________________________

## ❓ Альтернативы (отвергнутые)

| Вариант | Почему отвергли | |---------|-----------------| | **Упразднить ai_config_manager** | ❌
Убьёт hot reload, централизацию, HTTP API, 71 тест | | **HTTP-синхронные вызовы** | ❌ Жёсткие
временные связи, блокировка запроса | | **Kafka + Schema Registry** | ❌ Сложная инфраструктура (не
для одного разработчика) | | **Оставить как есть** | ❌ Нарушает best practices 2026, жюри не оценит
|

______________________________________________________________________

## ✅ Критерии успеха Фазы 1

- \[ \] `docker-compose up -d` работает без ошибок импорта
- \[ \] В `apps/` нет импортов других `apps/` (проверяется `boundary_checker.py`)
- \[ \] При отключении `ai_config_manager` сервисы переходят в degraded mode (не down!)
- \[ \] При создании проекта через API через ≤5 секунд публикуется `route.validated`
- \[ \] В RedisInsight видно событие `portfolio.events.project.created`
- \[ \] `tests/portfolio/test_events.py` проходит 100% (события)

______________________________________________________________________

## 🔗 Связанные документы

- **ADR-001:** Initial Design
- **ADR-022:** Microservices Principles
- **ADR-024:** Enhanced ConfigManager (async, metrics, multi-format)
- **README:** [apps/ai_config_manager/README.md](../../apps/ai_config_manager/README.md)

______________________________________________________________________

## 📝 История изменений

- **2026-05-20:** Первая версия (Вариант 1.5 — упразднение ai_config_manager) ❌ **ОШИБКА**
- **2026-06-13:** Обновлённая версия (сохранение ai_config_manager как сервиса) ✅ **ПРАВИЛЬНО**

______________________________________________________________________

*ADR-023 принят 20 мая 2026 г., обновлён 13 июня 2026 г.*
