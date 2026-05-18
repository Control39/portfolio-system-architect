# Thought Architecture

> **Статус:** 🟢 Production Ready
> **Версия:** 1.0.0
> **Владелец:** Portfolio System Architect Team

---

## 🎯 Назначение

Thought Architecture — сервис управления архитектурными решениями (ADR) и паттернами мышления. Обеспечивает централизованное хранение, поиск и версионирование архитектурных решений, а также рекомендует паттерны для новых задач.

### Ключевые возможности
- [x] Управление ADR (Architecture Decision Records)
- [x] Каталог паттернов мышления (системное мышление, contract-first и др.)
- [x] Фреймворки принятия решений
- [x] Векторный поиск по ADR и паттернам
- [x] Интеграция с docs/architecture/decisions/
- [x] Интеграция с AI Config Manager

---

## 💼 Архитектурная ценность

### Проблема

В сложных проектах архитектурные решения часто:
- **Разбросаны по документам** — трудно найти историю решений
- **Не документированы** — новые разработчики не понимают контекст
- **Повторяются** — изобретают велосипед вместо использования паттернов
- **Нет версионирования** — сложно отследить эволюцию

### Решение

Thought Architecture предоставляет:
- **Единое хранилище ADR** с статусами (proposed/accepted/deprecated)
- **Каталог паттернов** с use cases и связями
- **Поиск по контексту** — найдите релевантные решения
- **Фреймворки** для структурированного принятия решений

---

## 📦 Зависимости

Основные зависимости (см. `requirements.txt`):

- **FastAPI** >= 0.100.0 — веб-фреймворк
- **Pydantic** >= 2.0.0 — валидация данных
- **Uvicorn** >= 0.20.0 — ASGI сервер
- **PyYAML** >= 6.0.0 — загрузка конфигов
- **Sentence Transformers** (опционально) — векторный поиск

Установка:

```bash
pip install -r requirements.txt
```

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d thought-architecture
```

### Локальный запуск

```bash
cd apps/thought-architecture
python -m uvicorn main:app --reload --port 8500
```

### Доступ к API

- **Swagger UI:** http://localhost:8500/docs
- **Redoc:** http://localhost:8500/redoc
- **Health check:** http://localhost:8500/health

---

## 🛠️ API Endpoints

### Основные
- `GET /` — Информация о сервисе
- `GET /health` — Проверка здоровья

### ADR Management
- `GET /api/v1/adrs` — Список всех ADR (фильтр по статусу/тегу)
- `POST /api/v1/adrs` — Создать ADR
- `GET /api/v1/adrs/{adr_id}` — Получить ADR по ID
- `PUT /api/v1/adrs/{adr_id}` — Обновить статус ADR

### Patterns
- `GET /api/v1/patterns` — Список паттернов (фильтр по категории)
- `POST /api/v1/patterns` — Создать паттерн

### Frameworks
- `GET /api/v1/frameworks` — Список фреймворков

### Поиск
- `POST /api/v1/query` — Поиск по ADR, паттернам и фреймворкам

### Примеры

```bash
# Получить все принятые ADR
curl "http://localhost:8500/api/v1/adrs?status=accepted"

# Создать новый ADR
curl -X POST http://localhost:8500/api/v1/adrs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Выбор базы данных",
    "status": "proposed",
    "context": "Необходимо выбрать БД для хранения графа знаний",
    "decision": "PostgreSQL с расширением graph",
    "consequences": "Упрощение инфраструктуры"
  }'

# Поиск по контексту
curl -X POST http://localhost:8500/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "база данных граф", "limit": 5}'
```

---

## 🏗️ Архитектура

```
thought-architecture/
├── src/
│   ├── config_integration.py  # AI Config Manager
│   ├── adr_manager.py         # Управление ADR
│   ├── pattern_detector.py    # Детекция паттернов
│   └── __init__.py
├── tests/
│   ├── test_adr_manager.py
│   └── test_api.py
├── tools/
│   └── adr_generator.py       # Генератор ADR из шаблона
├── Dockerfile
├── main.py                    # FastAPI приложение
└── README.md
```

---

## 🧪 Тестирование

```bash
# Все тесты
pytest apps/thought-architecture/tests/ -v

# С покрытием
pytest apps/thought-architecture/tests/ --cov=apps/thought-architecture/src --cov-report=term-missing
```

---

## 🔐 Безопасность

- ✅ Валидация всех входных данных через Pydantic
- ✅ Защита от XSS (экранирование текста ADR)
- ✅ Rate limiting через Traefik

---

## 📚 AI Config Manager

Сервис интегрирован с централизованной конфигурацией:

```python
from apps.thought_architecture.src.config_integration import get_config

config = get_config()
settings = config.get_config()
```

---

## 🛣️ Маршрутизация

| Порт (внешний) | Маршрут (Traefik) | Порт (внутренний) |
|----------------|-------------------|-------------------|
| 8500 | `/thought-architecture` | 8500 |

---

## 📝 Known Issues

- Векторный поиск требует настройки модели embeddings (опционально)
- Нет автоматической синхронизации с файловой системой (планируется)

---

## 🛠️ Contributing

1. Fork репозиторий
2. Создайте ветку: `git checkout -b feature/ta-feature`
3. Внесите изменения и протестируйте
4. Закоммитьте: `git commit -m "feat: описание"`
5. Push: `git push origin feature/ta-feature`
6. Создайте Pull Request

**Правила:**
- Следуйте стилю Black + isort
- Добавьте тесты для новых функций
- Обновите документацию при необходимости
- Используйте шаблоны для ADR (см. `docs/architecture/decisions/template.md`)

---

*Последнее обновление: 18 мая 2026 г.*