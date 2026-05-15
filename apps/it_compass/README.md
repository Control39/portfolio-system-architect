# IT Compass

> **Статус:** Production Ready
> **Порт:** 8501
> **Маршрут:** `/it-compass`

---

## 🎯 Назначение

Методология объективного измерения компетенций через 83 проверочных маркера в 19 IT-доменах с поддержкой карьерного развития.

---

## 🏗️ Архитектура

### Технологии
- **Язык:** Python 3.10+
- **Фреймворк:** Streamlit (UI) + FastAPI (API)
- **База данных:** PostgreSQL 16 (опционально)
- **Контейнеризация:** Docker + Docker Compose

### Зависимости
- **PostgreSQL 16** — хранение прогресса (опционально)
- **Streamlit** — интерактивный UI
- **Traefik** — API шлюз

### Структура
```
it_compass/
├── src/
│   ├── api/          # API эндпоинты
│   ├── core/         # Методология (маркеры, трекинг)
│   └── models/       # Pydantic модели
├── tests/            # 46 тестов (100% покрытие)
├── app.py            # Streamlit UI
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start

### Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск только it-compass
docker-compose up -d it-compass

# Проверка состояния
docker-compose ps
```

### Локальный запуск (для разработки)

```bash
# Активация виртуального окружения
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск Streamlit UI
streamlit run app.py

# Или запуск API
uvicorn src.main:app --reload --port 8501
```

### Доступ к сервису

- **Через Traefik:** `http://localhost/it-compass`
- **Прямой доступ:** `http://localhost:8501`
- **Streamlit UI:** Открывается в браузере автоматически

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| GET   | `/health` | Health check | ❌ |
| GET   | `/_stcore/health` | Streamlit health | ❌ |
| GET   | `/api/v1/markers` | Получить все маркеры | ❌ |
| POST  | `/api/v1/tracker/update` | Обновить маркер | ✅ |
| GET   | `/api/v1/tracker/progress` | Прогресс пользователя | ✅ |
| POST  | `/api/v1/tracker/recommendations` | Рекомендации | ✅ |

### Примеры запросов

#### Health Check
```bash
curl http://localhost:8501/_stcore/health
# {"status": "ok"}
```

#### Получить маркеры компетенций
```bash
curl http://localhost:8501/api/v1/markers
# [
#   {"id": "dev_001", "name": "Python", "domain": "Development", "level": "junior"},
#   ...
# ]
```

#### Обновить маркер
```bash
curl -X POST http://localhost:8501/api/v1/tracker/update \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "marker_id": "dev_001",
    "level": "middle",
    "evidence": "Проект X на Python"
  }'
```

#### Прогресс пользователя
```bash
curl http://localhost:8501/api/v1/tracker/progress?user_id=user123 \
  -H "Authorization: Bearer <JWT_TOKEN>"
# {"overall_progress": 65%, "domain_breakdown": {...}, "recommendations": [...]}
```

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — секреты не логируются
- [x] **Валидация входных данных** — Pydantic модели для всех запросов
- [x] **JWT аутентификация** — интеграция с `auth_service`
- [ ] **Защита от XSS** — санитизация пользовательского ввода
- [ ] **Rate Limiting** — ограничение через Traefik

### Аутентификация

- **Метод:** JWT
- **Интеграция:** `auth_service`
- **Роли:** admin, user, career_counselor

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты с покрытием
pytest tests/ --cov=. --cov-report=term-missing

# Конкретный файл
pytest tests/test_tracker_real.py -v

# Сгенерировать HTML отчёт
pytest tests/ --cov=. --cov-report=html
# Открыть: htmlcov/index.html
```

### Покрытие кода

| Модуль | Покрытие | Статус |
|--------|----------|--------|
| `api/` | ~90% | ✅ |
| `core/` | ~80% | ✅ |
| **Всего** | **~85%** | **✅** |

**Цель:** ≥80% покрытие для production-ready сервисов

### Типы тестов

- **Юнит-тесты** — изолированное тестирование маркеров (28 тестов)
- **Интеграционные тесты** — API endpoints (10 тестов)
- **UI тесты** — Streamlit компоненты (8 тестов)

---

## 📊 Мониторинг

### Метрики

- **Prometheus:** `http://localhost:9090/targets`
- **Grafana:** `http://localhost:3000` (дашборд IT Compass)

### Логи

```bash
# Логи сервиса
docker-compose logs -f it-compass

# Логи с временными метками
docker-compose logs -f --tail=100 it-compass
```

### Health Check

```bash
curl http://localhost:8501/_stcore/health
# {"status": "ok", "streamlit_version": "1.32.0"}
```

---

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию | Обязательная |
|------------|----------|----------------------|--------------|
| `LOG_LEVEL` | Уровень логирования | `INFO` | ❌ |
| `DATABASE_URL` | URL базы данных | - | ⚠️ (если persistence) |
| `MARKERS_FILE` | Путь к JSON с маркерами | `./data/markers.json` | ❌ |
| `JWT_SECRET` | Секрет для JWT | `dev-secret` | ✅ |

### Методология

**83 маркера в 19 доменах:**

| Домен | Маркеры | Пример |
|-------|---------|--------|
| Development | 15 | Python, JavaScript, Docker |
| DevOps | 10 | Kubernetes, CI/CD, Monitoring |
| Security | 8 | OWASP, Cryptography |
| ... | ... | ... |

**Уровни сложности:**
- **Junior** — базовые знания
- **Middle** — практический опыт
- **Senior** — архитектурное мышление

---

## 📝 История изменений

| Версия | Дата | Изменения | Автор |
|--------|------|-----------|-------|
| 0.1.0 | 2026-05-15 | Initial MVP (46 тестов, 85% покрытие) | [YourName] |
| | | | |

---

## 🤝 Вклад

См. [CONTRIBUTING.md](../../CONTRIBUTING.md) для правил контрибуции.

### Задачи для контрибьюторов

- [ ] Добавить 5 новых доменов
- [ ] Реализовать export отчётов (PDF/Excel)
- [ ] Улучшить coverage до 90%
- [ ] Добавить геймификацию (бейджи, лидерборд)

---

## 📚 Дополнительные ресурсы

- [Архитектура проекта](../../ARCHITECTURE.md)
- [Быстрый старт](../../QUICK_START.md)
- [Методология IT-Compass](./docs/methodology.md)
- [Безопасность](../../SECURITY.md)

---

## 🐛 Известные проблемы

См. [KNOWN_ISSUES.md](../../docs/KNOWN_ISSUES.md) для списка известных проблем.

---

*Документ сгенерирован автоматически. Последнее обновление: 15 мая 2026 г.*
