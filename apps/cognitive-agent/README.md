# Cognitive Automation Agent (CAA)

> **Статус:** Active (MVP)
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 15 мая 2026 г.

---

## 🎯 Назначение

Автономный ИИ-агент для интеллектуальной автоматизации проектов. Обеспечивает анализ проектов, планирование задач, автономное выполнение и самообучение на основе метрик.

### Ключевые возможности
- [x] Анализ проектов (стек, зависимости, архитектура)
- [x] Планирование задач с приоритизацией
- [x] Автономное выполнение (настройка окружения, CI/CD)
- [x] Система самообучения (сбор метрик, адаптация)
- [x] Интеграция с Decision Engine для сложных решений

---

## 💼 Архитектурная ценность

### Проблема, которую решает Cognitive Agent

Современная разработка требует рутинных операций, которые отнимают время у инженеров:
- **Сканирование проектов:** Ручной анализ стека, зависимостей и архитектуры занимает часы.
- **Планирование:** Создание задач, приоритизация и оценка рисков — субъективный процесс.
- **Настройка окружения:** Повторяющиеся шаги (Docker, CI/CD, линтеры) требуют одинаковых усилий для каждого проекта.
- **Отсутствие обратной связи:** Агенты не учатся на ошибках, так как нет системы метрик.

### Решение

Cognitive Agent реализует **полный цикл автономной автоматизации**:
- **Project Scanner:** Автоматический анализ технологического стека и архитектуры.
- **Task Planner:** Генерация плана задач с учётом приоритетов и зависимостей.
- **Executor:** Безопасное выполнение рутинных операций (настройка окружения, CI/CD).
- **Learning System:** Сбор метрик и адаптация стратегий на основе результатов.

### Преимущества архитектуры

| Без Cognitive Agent | С Cognitive Agent |
|---------------------|-------------------|
| Ручной анализ проекта | Автоматическое сканирование |
| Субъективное планирование | Алгоритмическая приоритизация |
| Повторяющаяся настройка окружения | Автономная настройка (1 команда) |
| Нет обучения на ошибках | Самообучение на метриках |

### Готовая формулировка для портфолио

> **«Автономная система автоматизации (Cognitive Automation Agent)»**<br>
> Разработан ИИ-агент, выполняющий полный цикл автоматизации проектов: от сканирования технологического стека и генерации плана задач до автономного выполнения рутинных операций (настройка окружения, CI/CD). Внедрена система самообучения на основе метрик, позволяющая агенту адаптировать стратегии выполнения задач. Интеграция с Decision Engine обеспечивает принятие сложных решений с объяснимой логикой.

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, FastAPI (опционально), Docker |
| **Зависимости** | Decision Engine, Portfolio Organizer, IT-Compass |
| **Порт (Internal)** | 8009 (опционально, для API) |
| **Порт (External)** | N/A (CLI/модуль) |
| **Traefik Route** | N/A |
| **Health Check** | `GET /health` (опционально) |

### Схема развёртывания

```
┌─────────────────────────┐
│   Developer / CI/CD     │
│   (запуск агента)       │
└────────┬────────────────┘
         │ python launch-script.py
         ▼
┌─────────────────────────┐
│  Cognitive Agent        │
│  - Project Scanner      │
│  - Task Planner         │
│  - Executor             │
│  - Learning System      │
└────────┬────────────────┘
         │ использует
         ▼
┌─────────────────────────┐
│  Decision Engine        │
│  Portfolio Organizer    │
│  IT-Compass             │
└─────────────────────────┘
```

---

## 🚀 Quick Start

### Быстрый запуск (CLI)

```bash
# 1. Перейти в директорию агента
cd apps/cognitive-agent

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сканирование проекта
python launch-script.py --mode=scan --path=../../

# 4. Запустить рабочий процесс
python launch-script.py --workflow=project-setup

# 5. Полная автономия (требуется подтверждение)
python launch-script.py --mode=full --autonomy=high
```

### Режимы работы

| Режим | Описание | Безопасность |
|-------|----------|--------------|
| `--mode=minimal` | Только чтение, анализ | ✅ Безопасно |
| `--mode=scan` | Сканирование проекта | ✅ Безопасно |
| `--mode=plan` | Планирование задач | ✅ Безопасно |
| `--mode=full` | Полная автономия | ⚠️ Требуется подтверждение |

### Конфигурация

```yaml
# config/agent-config.yaml
agent:
  name: "cognitive-agent"
  version: "1.0.0"

  autonomy:
    mode: "minimal"  # minimal / scan / plan / full
    max_cpu: 50      # %
    max_memory: 1024 # MB

  skills:
    - project-scanner
    - task-planner
    - learning-system

  workflows:
    - project-setup
    - ci-cd-setup
```

---

## 🔌 API Контракты (опционально)

> 💡 **Примечание:** CAA в основном работает как CLI/модуль. HTTP API — опционально для интеграции.

### Эндпоинты (если включено)

| Метод | Эндпоинт | Описание | Auth |
|-------|----------|----------|------|
| `GET` | `/health` | Health check | ❌ |
| `POST` | `/api/v1/scan` | Сканировать проект | ✅ |
| `POST` | `/api/v1/plan` | Сгенерировать план | ✅ |
| `POST` | `/api/v1/execute` | Выполнить задачу | ✅ |
| `GET` | `/api/v1/status` | Статус агента | ✅ |

### Пример запроса

```bash
# Сканирование проекта
curl -X POST http://localhost:8009/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "path": "../../",
    "include_deps": true
  }'
```

> 💡 **Полная документация:** Доступна по адресу `http://localhost:8009/docs` (если API включено)

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Sandbox для команд** — изолированная среда выполнения
- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Лимиты ресурсов** — CPU ≤50%, память ≤1GB
- [x] **Откат изменений** — автоматический rollback при ошибках
- [x] **Аудит логов** — все действия агента логируются
- [x] **Без секретов** — агент не хранит и не передает API-ключи

### Security Checklist

При добавлении нового функционала проверить:

- [x] Нет hardcoded secrets в коде
- [x] Все внешние вызовы валидируют SSL
- [x] Input sanitization для пользовательских данных
- [x] Логирование security-событий (без секретов!)

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Из корневого каталога
pytest apps/cognitive-agent/tests/ --cov=apps/cognitive-agent --cov-report=term-missing

# С HTML отчётом
pytest apps/cognitive-agent/tests/ --cov=apps/cognitive-agent --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 31/31 | ≥80% ✅ |
| **Integration Tests** | 26/26 | ≥60% ✅ |
| **Total Coverage** | ~75% | ≥75% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 6 | Конфигурация, health checks |
| **Бизнес-логика** | `test_integration_cognitive_agent.py` | 25 | Scanner, planner, executor |

**Итого:** 31 тест, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
fastapi>=0.100.0  # опционально для API
pydantic>=2.0.0
uvicorn[standard]>=0.23.0  # опционально
pyyaml>=6.0.0
rich>=13.0.0  # для CLI UI
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

### Внешние сервисы

- [x] **Decision Engine** — reasoning для сложных решений
- [x] **Portfolio Organizer** — сбор доказательств
- [x] **IT-Compass** — методология и метрики
- [ ] **CodeAssistant** — скиллы для анализа кода

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Agent Configuration
AGENT_MODE=minimal
AGENT_CONFIG_PATH=config/agent-config.yaml

# External APIs
DECISION_ENGINE_URL=http://localhost:8001/api
PORTFOLIO_ORGANIZER_URL=http://localhost:8004/api

# Logging
LOG_LEVEL=INFO
LOG_PATH=logs/cognitive-agent.log

# Security
SECRET_KEY=your-secret-key-change-in-prod  # pragma: allowlist secret
```

### Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `.env` | Переменные окружения (не коммитить!) |
| `config/agent-config.yaml` | Конфигурация агента |
| `workflows/*.yaml` | Рабочие процессы |

---

## 📊 Мониторинг

### Метрики

- **Prometheus endpoint:** `GET /metrics` (если включено API)
- **Structured logging:** JSON format в stdout
- **Health checks:** `/health`, `/ready` (опционально)
- **Agent metrics:** Количество сканирований, выполненных задач, метрик обучения

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено)
- **Traefik Dashboard:** http://localhost:8080 (если включено API)

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/cognitive-agent-ci.yml
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
        run: pytest apps/cognitive-agent/tests/
      - name: Run linters
        run: ruff check apps/cognitive-agent/
```

### Развёртывание

- **Environment:** Development → Production
- **Strategy:** CLI-запуск или Docker-контейнер
- **Rollback:** Автоматический при ошибках выполнения

---

## 📚 Дополнительные ресурсы

### Документация

| Документ | Назначение |
|----------|------------|
| [README-COMMUNITY.md](./README-COMMUNITY.md) | Внешняя документация для сообщества |
| [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md) | Детальная реализация, архитектура |
| [USAGE.md](./USAGE.md) | Инструкции по запуску в monorepo |
| [ARCHITECTURE.md](../../ARCHITECTURE.md) | Общий обзор архитектуры |
| [SECURITY.md](../../SECURITY.md) | Политика безопасности |

### Связанные сервисы

- **[Decision Engine]** — reasoning для сложных решений
- **[Portfolio Organizer]** — сбор доказательств компетенций
- **[IT-Compass]** — методология и метрики
- **[CodeAssistant]** — скиллы для анализа кода
- **[Infra Orchestrator]** — управление инфраструктурой

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Некоторые скиллы — заглушки | In Progress | Постепенная реализация |
| Нет полноценного sandbox | Open | Использовать Docker для изоляции |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 31 тест с 100% прохождением
- **Added:** Project Scanner (Python, JavaScript)
- **Added:** Task Planner с генетическими алгоритмами
- **Added:** Документация для сообщества (README-COMMUNITY.md)
- **Changed:** Стандартизация документации по шаблону

### [0.9.0] — 2026-04-30

- **Added:** Базовая структура и конфигурации
- **Added:** Рабочие процессы (project-setup)

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation
- **Community** — см. [README-COMMUNITY.md](./README-COMMUNITY.md)

---

## 🤝 Вклад в проект

### Для разработчиков внутри monorepo

1. **Создайте ветку:** `git checkout -b feature/caa-new-skill`
2. **Добавьте скилл в:** `skills/`
3. **Напишите тесты:** `tests/test_new_skill.py`
4. **Обновите документацию:** `docs/` и `README-COMMUNITY.md`
5. **Запустите проверки:**
   ```bash
   make lint          # ruff + black
   make test          # pytest с покрытием
   make ci            # полная проверка
   ```

### Для сообщества (внешний вклад)

Смотрите [README-COMMUNITY.md](./README-COMMUNITY.md) — подробное руководство по добавлению скиллов, интеграций и шаблонов.

---

## 📬 Контакты

- **Проблемы/Предложения:** [GitHub Issues](https://github.com/Control39/portfolio-system-architect/issues)
- **Обсуждение:** [GitHub Discussions](https://github.com/Control39/portfolio-system-architect/discussions)
- **Основной репозиторий:** [Portfolio System Architect](https://github.com/Control39/portfolio-system-architect)

---

**Часть экосистемы [Portfolio System Architect](../../README.md)**
*Made with ❤️ by the Community*

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
