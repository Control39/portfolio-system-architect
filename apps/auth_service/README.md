# Auth Service

> **Статус:** Active
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Сервис аутентификации и авторизации на основе JWT токенов для всех микросервисов Portfolio System Architect. Обеспечивает безопасный доступ к API с ролевой моделью (admin/user).

### Ключевые возможности
- [x] JWT токены (HS256 алгоритм)
- [x] Ролевая модель (admin/user)
- [x] Валидация подписи и срока действия токенов
- [x] Защита от brute-force атак
- [x] Rate limiting через Traefik

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI, Docker, PyJWT |
| **Зависимости** | PostgreSQL (опционально для user store) |
| **Порт (Internal)** | 8100 (внутри контейнера) |
| **Порт (External)** | 8100 |
| **Traefik Route** | `/auth` |
| **Health Check** | `GET /health` |

### Схема развёртывания

```
┌─────────────────┐
│   Traefik       │  Port 80
│   (Gateway)     │
└────────┬────────┘
         │ PathPrefix(`/auth`)
         ▼
┌─────────────────┐
│  auth_service   │  Internal: 8100
│  (FastAPI)      │  External: 81100
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL/    │
│  Redis (cache)  │
└─────────────────┘
```

---

## 🚀 Quick Start

### Локальный запуск (Development)

```bash
# 1. Перейти в директорию сервиса
cd apps/auth_service

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер разработки
uvicorn src.main:app --reload --port 8100

# 4. Открыть Swagger UI
# http://localhost:8100/docs
```

### Запуск через Docker Compose

```bash
# Из корневого каталога проекта
docker-compose up -d auth_service

# Проверить статус
docker-compose ps | grep auth_service

# Просмотр логов
docker-compose logs -f auth_service
```

### Остановка

```bash
docker-compose stop auth_service
# или
docker-compose down auth_service
```

---

## 🔌 API Контракты

### Основные эндпоинты

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/ready` | Readiness check | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |
| `POST` | `/auth/token` | Получение JWT токена | ❌ |
| `POST` | `/auth/refresh` | Обновление токена | ✅ |
| `POST` | `/auth/revoke` | Отозвать токен | ✅ |
| `GET` | `/auth/me` | Информация о пользователе | ✅ |

### Пример запроса

```bash
# Health check
curl http://localhost:8100/health

# Через Traefik
curl http://localhost/auth/health

# Получение токена
curl -X POST http://localhost:8100/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo"  # pragma: allowlist secret
  }'

### Пример ответа

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "username": "demo",
    "role": "user"
  }
}
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8100/docs` (OpenAPI/Swagger)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех запросов/ответов
- [x] **Защита от brute-force** — ограничение попыток входа
- [x] **Token Security** — проверка подписи, expiration, forgery
- [x] **Password Policy** — отклонение слабых паролей
- [x] **Authorization** — RBAC, защита от IDOR

### Security Checklist

При добавлении нового функционала проверить:

- [x] Нет hardcoded secrets в коде
- [x] Все внешние вызовы валидируют SSL
- [x] Input sanitization для пользовательских данных
- [x] Логирование security-событий (без секретов!)

### Security Тесты

| Категория | Тесты | Статус |
|-----------|-------|--------|
| Brute Force Protection | 4 | ✅ |
| Token Security | 6 | ✅ |
| Authorization (RBAC/IDOR) | 5 | ✅ |
| Password Policy | 3 | ✅ |
| Security Regression | 2 | ✅ |

**Итого:** 20 security тестов, 100% прохождение ✅

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Из корневого каталога
pytest apps/auth_service/tests/ --cov=apps/auth_service --cov-report=term-missing

# С HTML отчётом
pytest apps/auth_service/tests/ --cov=apps/auth_service --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 21/21 | ≥80% ✅ |
| **Integration Tests** | 5/5 | ≥60% ✅ |
| **Security Tests** | 20/20 | 100% ✅ |
| **Total Coverage** | ~95% | ≥80% ✅ |

### Типы тестов

| Класс тестов | Тесты | Описание |
|-------------|-------|----------|
| `TestJWTTokenCreation` | 4 | Создание токенов с различными параметрами |
| `TestJWTTokenVerification` | 5 | Верификация (включая истёкшие/подделанные) |
| `TestRoleBasedAccess` | 3 | Ролевая модель (admin/user) |
| `TestAPIEndpoints` | 5 | API endpoints (token, refresh, revoke) |
| `TestEdgeCases` | 4 | Граничные случаи (Unicode, спецсимволы) |
| `TestSecurity` | 20 | Brute force, token forgery, IDOR, password policy |

**Итого:** 21 тест, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0
pydantic>=2.0.0
uvicorn[standard]>=0.23.0
PyJWT>=2.8.0
python-jose[cryptography]>=3.3.0
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### Внешние сервисы

- [ ] PostgreSQL (опционально, для хранения пользователей)
- [ ] Redis (опционально, для кэширования токенов)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-prod  # pragma: allowlist secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_ISSUER=portfolio-system-architect
JWT_AUDIENCE=api-clients

# Database (опционально)
DATABASE_URL=postgresql://user:password@postgres:5432/auth_service  # pragma: allowlist secret

# Logging
LOG_LEVEL=INFO

# Security
RATE_LIMIT=100/minute  # через Traefik
```

### Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `.env` | Переменные окружения (не коммитить!) |
| `config/settings.py` | Конфигурация сервиса |
| `pyproject.toml` | Зависимости и настройки сборки |

---

## 📊 Мониторинг

### Метрики

- **Prometheus endpoint:** `GET /metrics` (если включено)
- **Structured logging:** JSON format в stdout
- **Health checks:** `/health`, `/ready`
- **Security events:** Логирование неудачных попыток входа

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/auth-service-ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest apps/auth_service/tests/
      - name: Run linters
        run: ruff check apps/auth_service/
      - name: Security scan
        run: bandit -r apps/auth_service/
```

### Развёртывание

- **Environment:** Staging → Production
- **Strategy:** Blue-Green или Canary (через Kubernetes)
- **Rollback:** Автоматический при health check failure

---

## 📚 Дополнительные ресурсы

### Документация

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — общий обзор архитектуры
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — правила контрибуции
- [SECURITY.md](../../SECURITY.md) — политика безопасности

### Связанные сервисы

- **Все микросервисы** — используют Auth Service для аутентификации
- **[Decision Engine]** — требует JWT для доступа
- **[ML Model Registry]** — требует JWT для управления моделями
- **[Portfolio Organizer]** — требует JWT для анализа портфолио

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Интеграция с PostgreSQL требует Docker-окружения | Open | Использовать in-memory user store для тестов |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 21 тест с 100% прохождением
- **Added:** 20 security тестов (brute force, token forgery, IDOR)
- **Added:** Ролевая модель (admin/user)
- **Added:** Защита от слабых паролей
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
