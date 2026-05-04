# 🎯 QUICK REFERENCE CARD

> **TL;DR Guide** для быстрого доступа к основным командам и информации

---

## 📌 ТОП-5 ФАЙЛОВ ДЛЯ ЧТЕНИЯ

1. **[README.md](./README.md)** — Начни отсюда
2. **[ARCHITECTURE_MAP.md](./ARCHITECTURE_MAP.md)** — Структура проекта
3. **[DASHBOARD.md](./DASHBOARD.md)** — Метрики и статус
4. **[navigate.ps1](./navigate.ps1)** — Навигация по проекту
5. **[QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)** — Этот файл

---

## 🚀 ТОП КОМАНДЫ

```powershell
# Навигация
.\navigate.ps1 -Status              # Статус проекта
.\navigate.ps1 -List                # Все сервисы
.\navigate.ps1 -Map                 # Архитектурная карта
.\navigate.ps1 -Service <name>      # Перейти к сервису
.\navigate.ps1 -Tool <name>         # Перейти к инструменту

# Тестирование
pytest tests/ -v --cov              # Все тесты с coverage
pytest apps/<service>/tests/ -v     # Тесты одного сервиса
pytest tests/ --cov --cov-report=html  # HTML отчет

# Docker
docker-compose up                   # Запустить все сервисы
docker-compose logs -f              # Смотреть логи
docker-compose down                 # Остановить

# Kubernetes
kubectl apply -f deployment/k8s/    # Развернуть
kubectl get pods                    # Статус pods
kubectl logs -f <pod>               # Логи pod
kubectl port-forward svc/<name> 8080:80  # Доступ к сервису

# Git
git status                          # Статус
git add .                           # Добавить файлы
git commit -m "feat: ..."          # Коммит
git push                            # Отправить
```

---

## 📍 БЫСТРЫЕ ССЫЛКИ НА СЕРВИСЫ

```
PRODUCTION SERVICES:
├── Cognitive Agent     → apps/cognitive-agent
├── Decision Engine     → apps/decision-engine
├── IT-Compass          → apps/it_compass
├── Knowledge Graph     → apps/knowledge-graph
├── Portfolio Organizer → apps/portfolio_organizer
├── Career Development  → apps/career_development
├── Job Automation      → apps/job-automation-agent
├── Infra Orchestrator  → apps/infra-orchestrator
├── ML Registry         → apps/ml-model-registry
├── MCP Server          → apps/mcp-server
├── Auth Service        → apps/auth_service
├── AI Config Manager   → apps/ai-config-manager
├── Template Service    → apps/template-service
└── System Proof        → apps/system-proof

TOOLS:
├── Koda                → .koda/
├── Sourcecraft         → .sourcecraft/
├── Continue            → .continue/
└── Codeassistant       → codeassistant/

INFRASTRUCTURE:
├── Deployment          → deployment/
├── Docker              → docker/
├── Monitoring          → monitoring/
├── Config              → config/
└── Tests               → tests/
```

---

## 📊 КЛЮЧЕВЫЕ МЕТРИКИ

| Метрика | Значение | Статус |
|---------|----------|--------|
| **Code Coverage** | 95% | ✅ Отлично |
| **Сервисов в production** | 14 | ✅ Активны |
| **Инструментов анализа** | 4 | ✅ Работают |
| **Документов** | ~2000 | ⚠️ Нужна организация |
| **Тестов** | 1000+ | ✅ Хорошо |
| **Uptime** | 99.9% | ✅ Надежно |

---

## 🔗 МОНИТОРИНГ & DASHBOARDS

| Инструмент | URL | Статус |
|-----------|-----|--------|
| **Prometheus** | http://localhost:9090 | 🟢 Active |
| **Grafana** | http://localhost:3000 | 🟢 Active |
| **PostgreSQL** | localhost:5432 | 🟢 Active |
| **Elasticsearch** | localhost:9200 | 🟡 Configured |

**Grafana login**: `admin/admin`

---

## 🎯 БЫСТРЫЕ ДЕЙСТВИЯ

### Если нужно...

**...найти сервис**
```bash
./navigate.ps1 -Service <name>
# или
cd apps/<service-name>
```

**...запустить тесты**
```bash
cd apps/<service>
pytest tests/ -v --cov
```

**...посмотреть логи**
```bash
docker-compose logs -f <service>
# или
kubectl logs -f deployment/<service>
```

**...развернуть в production**
```bash
kubectl apply -f deployment/k8s/overlays/production/
```

**...проверить статус**
```bash
./navigate.ps1 -Status
# или
kubectl get pods
```

**...найти документацию**
```bash
./navigate.ps1 -Docs <keyword>
# или
cat docs/architecture/README.md
```

**...интегрировать инструмент**
```bash
# Koda
code .koda/

# Codeassistant
ls codeassistant/skills/

# Continue
code .continue/
```

---

## 📁 СТРУКТУРА В ОДНОМ ВЗГЛЯДЕ

```
portfolio-system-architect/
│
├── README.md                  ← Начни отсюда!
├── ARCHITECTURE_MAP.md        ← Вся архитектура
├── DASHBOARD.md              ← Метрики и статус
├── QUICK_REFERENCE_CARD.md   ← Этот файл
├── navigate.ps1              ← Навигация
│
├── apps/                     ← 14+ микросервисов
│   ├── cognitive-agent/
│   ├── decision-engine/
│   ├── it_compass/
│   ├── knowledge-graph/
│   ├── ... (and 10+ more)
│
├── deployment/               ← K8s manifests
├── docker/                   ← Dockerfiles
├── monitoring/               ← Prometheus + Grafana
├── docs/                     ← Документация
├── tests/                    ← Интеграционные тесты
│
├── .koda/                    ← Koda IDE
├── .continue/                ← Continue AI
├── .vscode/                  ← VS Code settings
├── codeassistant/            ← Code assistant
│
└── legacy/                   ← Старые версии
    ├── decision_engine_v1/
    └── ... (more)
```

---

## 🔑 КЛЮЧЕВЫЕ КОНЦЕПЦИИ

### Микросервисная архитектура
- **14 независимых сервисов** в production
- Каждый может развертываться отдельно
- Полная интеграция через APIs
- Zero downtime deployments

### Code Quality
- **95% test coverage** - отличный показатель
- **Automated testing** в CI/CD
- **Code reviews** перед merge
- **Security scanning** на каждый commit

### Monitoring & Observability
- **Prometheus** для метрик
- **Grafana** для визуализации
- **ELK** для логирования
- **Alertmanager** для оповещений

### Analysis Tools
- **Koda** - IDE с AI
- **Sourcecraft** - Code generation
- **Continue** - AI pair programming
- **Codeassistant** - Automated analysis

---

## 💡 СОВЕТЫ & ТРЮКИ

### Быстрая навигация
```bash
# Alias для быстрого доступа
alias nav='.\navigate.ps1'

# Использование
nav -Service cognitive-agent
nav -Status
nav -Map
```

### Просмотр всех сервисов одновременно
```bash
./navigate.ps1 -List              # Показывает все
```

### Быстрый доступ к документации
```bash
./navigate.ps1 -Docs architecture # Ищет по ключевому слову
```

### Проверка здоровья проекта
```bash
./navigate.ps1 -Status            # Полный отчет
```

---

## 🚨 ЕСЛИ ЧТО-ТО СЛОМАЛОСЬ

### Сервис не запускается?
```bash
# 1. Проверить логи
docker-compose logs <service>

# 2. Проверить конфиг
cat apps/<service>/config/*.yaml

# 3. Проверить зависимости
./navigate.ps1 -Service <service>

# 4. Перестартовать
docker-compose restart <service>
```

### Тесты падают?
```bash
# 1. Запустить один тест
pytest tests/test_specific.py -v -s

# 2. Проверить coverage
pytest tests/ --cov

# 3. Очистить и пересоздать
rm -rf __pycache__ .pytest_cache
pytest tests/ -v
```

### Проблемы с развертыванием?
```bash
# 1. Проверить K8s статус
kubectl get pods
kubectl describe pod <pod-name>

# 2. Проверить логи
kubectl logs -f deployment/<service>

# 3. Проверить resources
kubectl top pods
kubectl top nodes

# 4. Откатить
kubectl rollout undo deployment/<service>
```

---

## 📞 КУД ОБРАЩАТЬСЯ

1. **Документация** → [docs/](./docs/)
2. **Навигация** → `./navigate.ps1`
3. **Статус** → `./navigate.ps1 -Status`
4. **Помощь** → `./navigate.ps1 -Help`

---

## ⚡ ОДНА МИНУТА РЕФРЕШ

Если у тебя **1 минута** и нужно быстро разобраться:

```bash
# 1. Прочитай это
cat QUICK_REFERENCE_CARD.md

# 2. Посмотри структуру
./navigate.ps1 -Map

# 3. Проверь статус
./navigate.ps1 -Status

# 4. Перейди к нужному сервису
./navigate.ps1 -Service <name>

# Done! 🎉
```

---

## 🎓 ПО УРОВНЯМ УГЛУБЛЕНИЯ

### Новичок (5 минут)
1. Прочитать README.md
2. Запустить `./navigate.ps1 -Status`
3. Открыть Grafana (http://localhost:3000)

### Intermediate (30 минут)
1. Прочитать ARCHITECTURE_MAP.md
2. Перейти к интересующему сервису
3. Запустить его тесты

### Expert (2+ часа)
1. Изучить docs/architecture/
2. Изучить deployment/k8s/
3. Настроить CI/CD
4. Добавить новый сервис

---

## 🏆 ТУ УСПЕШНО СОЗДАЛА!

- ✅ 14+ микросервисов в production
- ✅ 95% code coverage
- ✅ Полная экосистема инструментов
- ✅ Comprehensive документацию
- ✅ Scaling infrastructure

**Это серьезно крутой проект!** 🚀

---

**Последнее обновление**: 2026-05-04  
**Статус**: 🟢 Production Ready  
**Версия**: 1.0 Stable

---

> **Помни**: У тебя уже есть всё, что нужно. Теперь просто используй `./navigate.ps1` чтобы найти то что нужно! 🎯
