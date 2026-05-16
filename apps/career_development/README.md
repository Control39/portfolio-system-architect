# Career Development

> **Статус:** MVP
> **Порт:** 8000
> **Маршрут:** `/career-dev`

---

## 🎯 Назначение

Система развития карьеры и отслеживания компетенций с интеграцией IT-Compass методологии.

---

## 🏗️ Архитектура

### Технологии
- **Язык:** Python 3.10+
- **Фреймворк:** FastAPI
- **База данных:** PostgreSQL 16 (опционально)
- **Контейнеризация:** Docker + Docker Compose

### Зависимости
- **PostgreSQL 16** — хранение профиля пользователя (опционально)
- **IT-Compass** — методология маркеров
- **Traefik** — API шлюз

### Структура
```
career_development/
├── src/
│   ├── api/          # API эндпоинты
│   ├── core/         # Бизнес-логика (CompetencyTracker)
│   └── models/       # Pydantic модели
├── tests/            # 56 тестов (80% покрытие)
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start

### Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск только career-development
docker-compose up -d career-development

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

# Запуск сервера
uvicorn src.main:app --reload --port 8000
```

### Доступ к сервису

- **Через Traefik:** `http://localhost/career-dev`
- **Прямой доступ:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| GET   | `/health` | Health check | ❌ |
| GET   | `/ready`  | Readiness check | ❌ |
| POST  | `/api/v1/users` | Добавить пользователя | ✅ |
| GET   | `/api/v1/users/{user_id}` | Профиль пользователя | ✅ |
| POST  | `/api/v1/skills` | Добавить навык | ✅ |
| GET   | `/api/v1/progress/{user_id}` | Прогресс пользователя | ✅ |
| POST  | `/api/v1/recommendations` | Рекомендации по развитию | ✅ |

### Примеры запросов

#### Health Check
```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "career-development"}
```

#### Добавить пользователя
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "Иван Петров",
    "role": "developer"
  }'
```

#### Добавить навык
```bash
curl -X POST http://localhost:8000/api/v1/skills \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "skill_name": "Python",
    "level": "middle",
    "evidence": "Проект X на Python"
  }'
```

#### Прогресс пользователя
```bash
curl http://localhost:8000/api/v1/progress/user123 \
  -H "Authorization: Bearer <JWT_TOKEN>"
# {
#   "overall_progress": 65%,
#   "skills": [{"name": "Python", "level": "middle", "progress": 80%}],
#   "recommendations": ["Изучить асинхронный Python", "Пройти курс по Docker"]
# }
```

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — секреты не логируются
- [x] **Валидация входных данных** — Pydantic модели для всех запросов
- [x] **JWT аутентификация** — интеграция с `auth_service`
- [ ] **Защита от IDOR** — проверка прав доступа к данным пользователя
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
pytest tests/test_competency_tracker.py -v

# Сгенерировать HTML отчёт
pytest tests/ --cov=. --cov-report=html
# Открыть: htmlcov/index.html
```

### Покрытие кода

| Модуль | Покрытие | Статус |
|--------|----------|--------|
| `api/` | ~85% | ✅ |
| `core/` | ~75% | ⚠️ |
| **Всего** | **~80%** | **✅** |

**Цель:** ≥80% покрытие для production-ready сервисов

### Типы тестов

- **Юнит-тесты** — изолированное тестирование CompetencyTracker (35 тестов)
- **Интеграционные тесты** — API endpoints (15 тестов)
- **Model тесты** — валидация Pydantic моделей (6 тестов)

---

## 📊 Мониторинг

### Метрики

- **Prometheus:** `http://localhost:9090/targets`
- **Grafana:** `http://localhost:3000` (дашборд Career Development)

### Логи

```bash
# Логи сервиса
docker-compose logs -f career-development

# Логи с временными метками
docker-compose logs -f --tail=100 career-development
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "career-development", "database": "connected"}
```

---

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Значение по умолчанию | Обязательная |
|------------|----------|----------------------|--------------|
| `LOG_LEVEL` | Уровень логирования | `INFO` | ❌ |
| `DATABASE_URL` | URL базы данных | - | ⚠️ (если persistence) |
| `IT_COMPASS_API` | URL IT-Compass сервиса | `http://it-compass:8501` | ❌ |
| `JWT_SECRET` | Секрет для JWT | `dev-secret` | ✅ |

### Бизнес-логика

**CompetencyTracker** — ядро сервиса:

- `add_user(user_id)` — добавить пользователя
- `add_skill(user_id, skill_name, level)` — добавить навык
- `update_skill_level(user_id, skill_name, level)` — обновить уровень
- `get_user_progress(user_id)` — прогресс пользователя
- `generate_progress_report(user_id)` — отчёт прогресса
- `check_competency_achievement(user_id, marker_id)` — проверка достижения
- `list_pending_markers(user_id)` — список недостиженных маркеров
- `calculate_progress(user_id)` — общий прогресс

---

## 📝 История изменений

| Версия | Дата | Изменения | Автор |
|--------|------|-----------|-------|
| 0.1.0 | 2026-05-14 | Initial MVP (56 тестов, 80% покрытие) | [YourName] |
| 0.2.0 | 2026-05-15 | Добавлен Dockerfile, обновлён README | [YourName] |
| | | | |

---

## 🤝 Вклад

См. [CONTRIBUTING.md](../../CONTRIBUTING.md) для правил контрибуции.

### Задачи для контрибьюторов

- [ ] Добавить экспорт отчётов (PDF/Excel)
- [ ] Реализовать интеграцию с IT-Compass API
- [ ] Улучшить coverage до 85%
- [ ] Добавить геймификацию (бейджи, лидерборд)

---

## 📚 Дополнительные ресурсы

- [Архитектура проекта](../../ARCHITECTURE.md)
- [Быстрый старт](../../QUICK_START.md)
- [IT-Compass методология](../it_compass/README.md)
- [Безопасность](../../SECURITY.md)

---

## 🐛 Известные проблемы

См. [KNOWN_ISSUES.md](../../docs/KNOWN_ISSUES.md) для списка известных проблем.

---

*Документ сгенерирован автоматически. Последнее обновление: 15 мая 2026 г.*
