# 🚀 Быстрый старт

**Цель:** Запустить всю систему за **5 минут**

---

## 📋 Предварительные требования

- ✅ Docker Desktop (версия ≥ 20.10)
- ✅ Python 3.10+ (для локальной разработки)
- ✅ PowerShell 7+ (для Windows)

---

## ⚡ Запуск всей системы (2 минуты)

### Шаг 1: Перейти в проект

```powershell
cd C:\repo
```

### Шаг 2: Запустить все сервисы

```powershell
docker compose up -d
```

**Что запустится:**
- 14 микросервисов (AI Config Manager, IT Compass, MCP Server, и др.)
- Prometheus + Grafana (мониторинг)
- Traefik (reverse proxy)

**Ожидание:** 2-3 минуты (первый запуск скачивает образы)

---

## ✅ Проверка работы

### Проверить контейнеры:

```powershell
docker ps
```

**Ожидаемый результат:** 15+ контейнеров в статусе `Up`

### Проверить health endpoints:

```powershell
# AI Config Manager
curl http://localhost:8000/health

# IT Compass
curl http://localhost:8501/_stcore/health

# MCP Server
curl http://localhost:8002/health
```

**Ожидаемый результат:**
```json
{"status": "healthy", "service": "ai-config-manager"}
```

---

## 🌐 Доступ к интерфейсам

| Сервис | URL | Логин/пароль |
|--------|-----|--------------|
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **IT Compass** | http://localhost:8501 | - |
| **AI Config Manager API** | http://localhost:8000/docs | - |
| **MCP Server API** | http://localhost:8002/docs | - |

---

## 🧪 Запуск тестов (локально)

### AI Config Manager:

```powershell
cd apps/ai_config_manager
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/ -v --cov=src
```

**Ожидаемый результат:**
```
============================= 71 passed in 0.77s ==============================
```

### IT Compass:

```powershell
cd apps/it_compass
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/ -v --cov=src
```

**Ожидаемый результат:**
```
============================= 50+ passed ==============================
```

---

## 📊 Мониторинг

### Запустить только мониторинг:

```powershell
docker compose -f docker-compose.monitoring.yml up -d
```

### Проверить Prometheus:

```powershell
# Открыть в браузере
start http://localhost:9090

# Проверить job'ы
# http://localhost:9090/targets
```

**Ожидаемый результат:** 12 job'ов в статусе `UP`

---

## 🛑 Остановка

### Остановить все контейнеры:

```powershell
docker compose down
```

### Остановить только мониторинг:

```powershell
docker compose -f docker-compose.monitoring.yml down
```

### Удалить все контейнеры и тома:

```powershell
docker compose down -v
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

### 3. Запустить сервис (пример: AI Config Manager):

```powershell
cd apps/ai_config_manager
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Открыть Swagger:

```powershell
start http://localhost:8000/docs
```

---

## 🐛 Решение проблем

### Проблема: Контейнеры не запускаются

**Решение:**
```powershell
# Проверить логи
docker compose logs

# Очистить Docker
docker compose down -v
docker system prune -a

# Перезапустить
docker compose up -d --build
```

### Проблема: Порт занят

**Решение:**
```powershell
# Найти процесс на порту 8000
netstat -ano | findstr :8000

# Убить процесс
taskkill /PID <PID> /F
```

---

## 📚 Следующие шаги

### После запуска:

1. **Прочитать ASSETS.md** — список всех активов
2. **Прочитать DEMO_GUIDE.md** — как показать работодателю
3. **Прочитать DASHBOARD.md** — статус проекта
4. **Открыть Grafana** — http://localhost:3000
5. **Открыть IT Compass** — http://localhost:8501

### Для углубления:

- [Архитектура](./ARCHITECTURE.md)
- [Методология IT Compass](./apps/it_compass/docs/METHODOLOGY.md)
- [Мониторинг](./monitoring/README.md)
- [Вклад в проект](./CONTRIBUTING.md)

---

## 🎯 Чеклист первого запуска

- [ ] Docker Desktop запущен
- [ ] `docker compose up -d` выполнился без ошибок
- [ ] `docker ps` показывает 15+ контейнеров
- [ ] Grafana доступна на http://localhost:3000
- [ ] IT Compass доступен на http://localhost:8501
- [ ] AI Config Manager API доступен на http://localhost:8000/docs
- [ ] Пройдены тесты в AI Config Manager (71 тест)
- [ ] Прочитан ASSETS.md
- [ ] Прочитан DEMO_GUIDE.md

---

*Документ автоматически обновляется при изменении проекта.*
