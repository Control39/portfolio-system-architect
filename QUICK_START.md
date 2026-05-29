## 🚀 QUICK_START

**Цель:** Запустить ключевые сервисы за **5 минут**

> ⚠️ **О состоянии:**  
> - 🟢 **12 сервисов** готовы к запуску через `docker-compose up -d`  
> - 🟡 **4 сервиса** в статусе WIP — требуют `--profile wip`  
> - 🔒 **0 критических уязвимостей** (Trivy + Bandit + CodeQL в CI/CD)

---

## 📋 Предварительные требования

- ✅ Docker Desktop (версия ≥ 20.10)
- ✅ Python 3.12+ (для локальной разработки)
- ✅ PowerShell 7+ (для Windows)
- ✅ curl или wget (для health checks)

---

## ⚡ Запуск стабильных сервисов (3 минуты)

### Шаг 1: Перейти в проект

```powershell
cd C:\repo
```

### Шаг 2: Запустить стабильные сервисы

```powershell
# Запускаем только сервисы без профиля (🟢 Ready)
docker-compose up -d `
  traefik `
  auth_service `
  it-compass `
  decision-engine `
  ml-model-registry `
  career-development `
  portfolio_organizer `
  system-proof `
  infra_orchestrator `
  ai_config_manager `
  chat_backend `
  knowledge_graph `
  postgres `
  redis
```

**Что запустится:**
| Сервис | Порт | Назначение |
|--------|------|-----------|
| `traefik` | 80, 8080 | Gateway + Dashboard |
| `auth_service` | 8100 | JWT-аутентификация |
| `it-compass` | 8501 | UI для трекинга компетенций (Streamlit) |
| `decision-engine` | 8001 | AI reasoning API |
| `ml-model-registry` | 8002 | Регистр моделей |
| `portfolio_organizer` | 8004 | Сбор доказательств |
| `system-proof` | 8003 | CoT storage |
| `infra_orchestrator` | 8200 | Управление сервисами |
| `ai_config_manager` | 8500 | Централизованная конфигурация |
| `chat_backend` | 8005 | WebSocket-чат |
| `knowledge_graph` | 8006 | Граф знаний |
| `postgres` | 5432 | База данных |
| `redis` | 6379 | Кэш и очереди |

**Ожидание:** 3-5 минут (первый запуск скачивает образы)

---

## 🧪 Запуск экспериментальных сервисов (опционально)

```powershell
# Запустить сервисы в статусе 🟡 WIP
docker-compose --profile wip up -d `
  cognitive_agent `
  job_automation_agent `
  thought_architecture `
  template_service `
  mcp_server
```

> ⚠️ Эти сервисы могут требовать дополнительной настройки (API-ключи, конфиги).

---

## ✅ Проверка работы

### Проверить контейнеры:

```powershell
docker-compose ps
```

**Ожидаемый результат:**
```
NAME                        STATUS                    PORTS
auth_service                Up (healthy)              0.0.0.0:8100->8100/tcp
it-compass                  Up (healthy)              0.0.0.0:8501->8501/tcp
decision-engine             Up (healthy)              0.0.0.0:8001->8001/tcp
postgres-db                 Up (healthy)              0.0.0.0:5432->5432/tcp
...
```

### Проверить health endpoints:

```powershell
# Auth Service (FastAPI)
curl http://localhost:8100/health
# → {"status":"healthy","service":"auth_service"}

# Decision Engine
curl http://localhost:8001/api/v1/status
# → HTTP 200

# IT-Compass (Streamlit — нет стандартного health)
curl -I http://localhost:8501
# → HTTP/1.1 200 OK

# Traefik dashboard
curl http://localhost:8080/api/http/routers
# → JSON со списком маршрутов
```

---

## 🌐 Доступ к интерфейсам

| Сервис | URL | Логин/пароль | Статус |
|--------|-----|--------------|--------|
| **Traefik Dashboard** | http://localhost:8080 | — | 🟢 |
| **IT-Compass UI** | http://localhost:8501 | — | 🟢 |
| **Decision Engine API** | http://localhost:8001/docs | — | 🟢 |
| **Auth Service API** | http://localhost:8100/docs | — | 🟢 |
| **ML Model Registry** | http://localhost:8002/docs | — | 🟢 |
| **Portfolio Organizer** | http://localhost:8004/docs | — | 🟢 |
| **System Proof** | http://localhost:8003/docs | — | 🟢 |
| **Infra Orchestrator** | http://localhost:8200/docs | — | 🟢 |
| **AI Config Manager** | http://localhost:8500/docs | — | 🟢 |
| **Chat Backend** | http://localhost:8005/docs | — | 🟢 |
| **Knowledge Graph** | http://localhost:8006/docs | — | 🟢 |
| **Cognitive Agent** | http://localhost:8008/docs | — | 🟡 WIP |
| **MCP Server** | http://localhost:8007/docs | — | 🟡 WIP |

> 🔹 **Через Traefik:** Все сервисы доступны также по пути `http://localhost/<service-name>`  
> Пример: `http://localhost/it-compass` → перенаправит на `it-compass:8501`

---

## 🧪 Запуск тестов (локально)

### Общий запуск (рекомендуется):

```powershell
cd C:\repo
pytest apps/auth_service apps/it_compass apps/decision_engine apps/portfolio_organizer apps/career_development apps/thought_architecture apps/infra_orchestrator -q --cov=apps --cov-report=term-missing
```

**Ожидаемый результат:**
```
779 passed, 21 skipped in XX.XXs
============================== 779 passed ==============================
```

### Тесты для одного сервиса (пример: IT-Compass):

```powershell
cd apps/it_compass
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/ -v --cov=src
```

---

## 📊 Мониторинг

### Проверить PostgreSQL:

```powershell
docker-compose exec postgres pg_isready -U ${POSTGRES_USER}
# → postgres:5432 - accepting connections
```

### Проверить Redis:

```powershell
docker-compose exec redis redis-cli ping
# → PONG
```

### Traefik logs:

```powershell
docker-compose logs -f traefik
```

---

## 🛑 Остановка

### Остановить стабильные сервисы:

```powershell
docker-compose down
```

### Остановить только WIP-сервисы:

```powershell
docker-compose --profile wip down
```

### Удалить все контейнеры и тома (осторожно!):

```powershell
docker-compose down -v
```

---

## 🔧 Локальная разработка

### 1. Создать виртуальное окружение:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Установить зависимости:

```powershell
pip install -r requirements-dev.txt
```

### 3. Запустить сервис (пример: Decision Engine):

```powershell
cd apps/decision_engine
# Убедись, что PYTHONPATH настроен
$env:PYTHONPATH = "/app:/app/src"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### 4. Открыть Swagger:

```powershell
start http://localhost:8001/docs
```

---

## 🐛 Решение проблем

### Проблема: "curl: command not found" в healthcheck

**Решение:** Добавь curl в Dockerfile сервиса:
```dockerfile
# apps/auth_service/Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

**Или замени healthcheck на Python:**
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8100/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Проблема: Сервис не видит импорты из src/

**Решение:** Убедись, что в docker-compose.yml и Dockerfile есть:
```yaml
environment:
  - PYTHONPATH=/app:/app/src
```
```dockerfile
ENV PYTHONPATH=/app:/app/src
```

### Проблема: PostgreSQL не готов, сервисы падают

**Решение:** Увеличь retry и добавь start_period:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
  interval: 10s
  timeout: 5s
  retries: 10
  start_period: 30s
```

### Проблема: Порт занят

**Решение:**
```powershell
# Найти процесс на порту 8001
netstat -ano | findstr :8001

# Убить процесс
taskkill /PID <PID> /F
```

### Проблема: Streamlit (IT-Compass) не отвечает на healthcheck

**Решение:** Streamlit не имеет стандартного `/health`. Используй:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8501')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 📚 Следующие шаги

### После запуска:

1. **Открыть IT-Compass** — http://localhost:8501 (самооценка навыков)
2. **Открыть Decision Engine** — http://localhost:8001/docs (AI reasoning)
3. **Прочитать ARCHITECTURE.md** — схема взаимодействий
4. **Прочитать docs/HIRING_BRIEF.md** — как показать работодателю

### Для углубления:

- [Архитектурные решения (ADR)](docs/architecture/decisions/)
- [Методология IT-Compass](apps/it_compass/docs/METHODOLOGY.md)
- [Мониторинг](monitoring/README.md)
- [Вклад в проект](CONTRIBUTING.md)

---

## 🎯 Чеклист первого запуска

- [ ] Docker Desktop запущен
- [ ] `docker-compose up -d` выполнился без критических ошибок
- [ ] `docker-compose ps` показывает 12+ контейнеров в статусе `Up` или `healthy`
- [ ] IT-Compass доступен на http://localhost:8501
- [ ] Decision Engine API доступен на http://localhost:8001/docs
- [ ] Auth Service API доступен на http://localhost:8100/docs
- [ ] PostgreSQL отвечает на `pg_isready`
- [ ] Redis отвечает на `redis-cli ping`
- [ ] Прочитан docs/HIRING_BRIEF.md

---

> *Документ отражает состояние на май 2026. Сервисы в статусе 🟡 WIP могут требовать дополнительной настройки. Подробности: [Таблица сервисов](#-доступ-к-интерфейсам)*































































