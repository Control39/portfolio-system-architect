# 🎯 Демо-гайд для работодателя

**Цель:** Показать production-ready экосистему за **5-10 минут**

---

## 🚀 Быстрый старт (2 минуты)

### Шаг 1: Показать метрики проекта (30 сек)

```powershell
# В корень репозитория
cd C:\repo

# Посчитать метрики
python scripts/collect_metrics.py
```

**Что показать:**
```
📊 Python Files: 1,247
🧪 Test Files: 200+
📦 Microservices: 14
📝 Lines of Code: 125k
🔗 Git Commits: 500+
```

---

### Шаг 2: Показать тесты (30 сек)

```powershell
# Запустить тесты AI Config Manager
cd apps/ai_config_manager
pytest tests/ -v --tb=short
```

**Что показать:**
```
============================= 71 passed in 0.77s ==============================
```

**Почему это важно:**
- ✅ **71 тест** — production-ready качество
- ✅ **100% пройдено** — стабильность
- ✅ **Docker 94.5MB** — оптимизация

---

### Шаг 3: Запустить мониторинг (1 мин)

```powershell
# Вернуться в корень
cd C:\repo

# Запустить Prometheus + Grafana
docker compose -f docker-compose.monitoring.yml up -d
```

**Проверить:**
```powershell
docker ps | Select-String "prometheus\|grafana\|alertmanager"
```

**Открыть в браузере:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

**Что показать:**
- ✅ **12 job'ов** настроено
- ✅ **25+ алертов** определено
- ✅ **Grafana дашборды** импортированы

---

### Шаг 4: Показать IT Compass (1 мин)

```powershell
# Запустить IT Compass
docker compose up -d it-compass

# Открыть UI
start http://localhost:8501
```

**Что показать:**
- ✅ **19 доменов** компетенций
- ✅ **83 маркера** (25 выполнено)
- ✅ **Streamlit UI** — карьерный трекинг

**Демонстрация:**
```
📊 Python: [███░░░░░░░] 37.5% (3/8)
📊 Docker: [█████░░░░░] 55.6% (5/9)
📊 Git: [███░░░░░░░░] 50% (3/6)
Общий прогресс: [███░░░░░░░░] 30.1% (25/83)
```

---

### Шаг 5: Показать API (1 мин)

```powershell
# Запустить AI Config Manager
docker compose up -d ai-config-manager

# Проверить health
curl http://localhost:8000/health
```

**Что показать:**
```json
{
  "status": "healthy",
  "service": "ai-config-manager",
  "version": "1.0.0"
}
```

**Открыть Swagger UI:**
```
start http://localhost:8000/docs
```

**Что показать:**
- ✅ **11 endpoints**
- ✅ **Документация** (ReDoc + Swagger)
- ✅ **Валидация** (Pydantic)

---

### Шаг 6: Показать документацию (30 сек)

```powershell
# Открыть DASHBOARD.md
start DASHBOARD.md
```

**Что показать:**
- ✅ **14 сервисов** со статусом
- ✅ **Мониторинг** (Prometheus/Grafana)
- ✅ **Покрытие тестами** (87%)

---

## 📊 Глубокое демо (10-15 минут)

### Раздел 1: Архитектура (3 мин)

**Открыть:** `ARCHITECTURE.md`

**Показать:**
```
┌─────────────────────────────────────────────────────┐
│              PORTFOLIO SYSTEM                       │
└─────────────────────────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
AI Config  MCP    IT Compass
Manager    Server   (Streamlit)
```

**Рассказать:**
- **14 микросервисов** — модульность
- **Docker + K8s** — production-ready
- **Monitoring** — observability

---

### Раздел 2: Методология IT Compass (3 мин)

**Открыть:** `apps/it_compass/docs/METHODOLOGY.md`

**Показать:**
```
19 доменов × 3 уровня = 83 маркера
- Specific (конкретные)
- Measurable (измеримые)
- Achievable (достижимые)
- Relevant (релевантные)
- Time-bound (ограниченные по времени)
```

**Рассказать:**
- **SMART-критерии** — объективность
- **Валидация** — доказательства
- **Приоритеты** — high/medium/low

---

### Раздел 3: Инфраструктура (2 мин)

**Открыть:** `deployment/k8s/`

**Показать:**
```yaml
# HPA (автомасштабирование)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Рассказать:**
- **HPA** — автомасштабирование по CPU
- **K8s** — оркестрация
- **Terraform** — IaC

---

### Раздел 4: Безопасность (2 мин)

**Открыть:** `src/security/secret_masking.py`

**Показать:**
```python
class SecretMasker:
    def mask_secrets(self, text: str) -> str:
        # Маскируем API ключи
        pattern = r'(api[_-]?key|secret|token)\s*[:=]\s*[\w-]+'
        return re.sub(pattern, r'\1=***MASKED***', text)
```

**Рассказать:**
- **Secret masking** — защита логов
- **No secrets in repo** — безопасность
- **Azure Key Vault** — управление секретами

---

### Раздел 5: CI/CD (2 мин)

**Открыть:** `.github/workflows/`

**Показать:**
```yaml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/ --cov=src
      - run: docker build -t my-service .
      - run: docker push my-service
```

**Рассказать:**
- **GitHub Actions** — автоматизация
- **pytest + coverage** — тесты
- **Docker** — контейнеризация

---

## 🎯 Ключевые сообщения для работодателя

### Для HR / Recruiter:

> "Я создала production-ready экосистему из **14 микросервисов** с **200+ тестами**, **87% покрытием**, и полным мониторингом (Prometheus + Grafana). Это не учебный проект — это **готовое решение** для enterprise."

**Доказательства:**
- ✅ ASSETS.md — список всех активов
- ✅ 71 тест в AI Config Manager (100% пройдено)
- ✅ Docker образы < 500MB (оптимизация)

---

### Для Technical Lead / Architect:

> "Архитектура построена на принципах **модульности** (14 независимых сервисов), **наблюдаемости** (Prometheus + Grafana + AlertManager), и **автоматизации** (CI/CD, K8s HPA). Все решения документированы через **ADR** (Architecture Decision Records)."

**Доказательства:**
- ✅ ARCHITECTURE.md — детальная архитектура
- ✅ docs/architecture/decisions/ — ADR
- ✅ monitoring/ — observability stack

---

### Для CTO / Hiring Manager:

> "Методология **IT Compass** превращает неопределённость в измеримые метрики: **19 доменов**, **83 маркера**, **SMART-критерии**. Это не просто трекинг навыков — это **система обратной связи** для карьеры с доказательной базой."

**Доказательства:**
- ✅ apps/it_compass/ — реализация методологии
- ✅ 25 выполненных маркеров (30.1% прогресс)
- ✅ DASHBOARD.md — объективные метрики

---

## 📋 Чеклист перед демонстрацией

### Подготовка (15 минут):

- [ ] `cd C:\repo` — перейти в проект
- [ ] `docker compose ps` — проверить контейнеры
- [ ] `docker compose -f docker-compose.monitoring.yml up -d` — запустить мониторинг
- [ ] `docker compose up -d it-compass` — запустить IT Compass
- [ ] `start http://localhost:3000` — открыть Grafana
- [ ] `start http://localhost:8501` — открыть IT Compass UI
- [ ] `start http://localhost:8000/docs` — открыть Swagger

### Открыть документы:

- [ ] `ASSETS.md` — список активов
- [ ] `DASHBOARD.md` — статус проекта
- [ ] `ARCHITECTURE.md` — архитектура
- [ ] `apps/it_compass/docs/METHODOLOGY.md` — методология

### Тесты:

- [ ] `cd apps/ai_config_manager && pytest tests/ -v` — показать 71 тест
- [ ] `cd apps/it_compass && pytest tests/ -v` — показать тесты IT Compass

---

## 🎁 Бонус: Скриншоты для резюме

### 1. Grafana Dashboard
```
monitoring/docs/screenshots/grafana-dashboard.png
```
**Что показать:** Prometheus + Grafana работают

### 2. IT Compass UI
```
apps/it_compass/docs/screenshots/ui.png
```
**Что показать:** 19 доменов, 83 маркера, прогресс

### 3. Swagger API
```
apps/ai_config_manager/docs/screenshots/swagger.png
```
**Что показать:** 11 endpoints, документация

### 4. Docker Containers
```
docker ps
```
**Что показать:** Все сервисы работают

---

## 💡 Советы для демонстрации

### Делай:
✅ **Начинай с метрик** — "14 сервисов, 200+ тестов, 87% покрытие"  
✅ **Показывай живое демо** — запускай контейнеры на глазах  
✅ **Говори о бизнес-ценности** — "production-ready, enterprise-ready"  
✅ **Упоминай методологию** — "IT Compass, SMART-критерии"  

### Не делай:
❌ **Не углубляйся в код** — показывай результат, не детали  
❌ **Не говори "учебный проект"** — это production-ready решение  
❌ **Не забывай про мониторинг** — это SRE экспертиза  
❌ **Не скрывай методологию** — это уникальная ценность  

---

## 📞 Следующие шаги после демо

### Если интересуют:

**Архитектура:**
- Отправь `ARCHITECTURE.md`
- Покажи `docs/architecture/decisions/`

**Методология:**
- Отправь `apps/it_compass/docs/METHODOLOGY.md`
- Покажи `ASSETS.md` (раздел "Бизнес-метрики")

**Инфраструктура:**
- Отправь `monitoring/README.md`
- Покажи `deployment/k8s/`

**Код:**
- Отправь `apps/ai_config_manager/README.md`
- Покажи тесты (`pytest tests/ -v`)

---

*Документ автоматически обновляется при изменении проекта.*
