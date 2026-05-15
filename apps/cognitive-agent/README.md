# Cognitive Automation Agent (CAA)

> **Автономный ИИ-агент для интеллектуальной автоматизации проектов**

Часть экосистемы [Portfolio System Architect](../../README.md) — когнитивной архитектуры, демонстрирующей трансформацию от нуля до 14 интегрированных микросервисов за 2 года.

---

## 📌 Быстрый доступ

| Для кого | Документ | Описание |
|----------|----------|----------|
| **Сообщество** | [📖 README-COMMUNITY.md](./README-COMMUNITY.md) | Внешняя документация, быстрый старт, вклад |
| **Разработчики** | [🔧 IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md) | Детальная реализация, архитектура, тесты |
| **Внутреннее использование** | [📋 USAGE.md](./USAGE.md) | Инструкции по запуску в рамках monorepo |

---

## 🎯 Назначение

**Cognitive Automation Agent** — автономная система для:
- 📊 **Анализа проектов** — определение стека, зависимостей, архитектурных паттернов
- 📋 **Планирования задач** — проактивное предсказание и приоритизация
- ⚡ **Автономного выполнения** — настройка окружения, CI/CD, оптимизация
- 🧠 **Самообучения** — адаптация алгоритмов на основе метрик

**Пример:** Открываете новый проект → агент за 2 минуты настраивает Docker, CI/CD, линтеры → вы начинаете кодить.

---

## 🏗️ Структура

```
cognitive-agent/
├── skills/                      # Основные навыки агента
│   ├── project-scanner/         # Анализ проекта (стек, зависимости)
│   ├── task-planner/            # Планирование и приоритизация
│   ├── cognitive-automation-agent/ # Ядро автономии
│   └── learning-system/         # Сбор метрик и адаптация
├── workflows/                   # Готовые сценарии
│   └── project-setup.yaml       # Автоматическая настройка проекта
├── config/                      # Конфигурации
│   └── agent-config.yaml        # Настройки автономности
├── src/                         # Исходный код (в разработке)
├── tests/                       # Тесты
├── data/                        # База данных метрик
├── logs/                        # Логи выполнения
└── reports/                     # Ежедневные отчеты
```

---

## 🚀 Запуск (в рамках monorepo)

### Предварительные требования

```bash
# Убедитесь, что Python 3.10+
python --version

# Активируйте виртуальное окружение проекта
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### Установка зависимостей

```bash
cd apps/cognitive-agent
pip install -r requirements.txt
```

### Запуск агента

```bash
# Минимальный режим (безопасный, только чтение)
python launch-script.py --mode=minimal

# Сканирование проекта
python launch-script.py --mode=scan --path=../../

# Запуск рабочего процесса
python launch-script.py --workflow=project-setup

# Полная автономия (требуется подтверждение в config)
python launch-script.py --mode=full --autonomy=high
```

### Тестирование

```bash
# Юнит-тесты
python -m pytest tests/ -v

# С покрытием
python -m pytest tests/ --cov=src --cov-report=html

# Интеграционные тесты
python -m pytest tests/test_integration_cognitive_agent.py -v
```

---

## ⚙️ Конфигурация

Основной конфиг: `config/agent-config.yaml`

```yaml
autonomy:
  level: high              # high, medium, low
  approval_required: false # false для доверенных паттернов
  trusted_patterns:
    - "*.test.*"
    - "requirements*.txt"
    - ".github/workflows/*"
    - "Dockerfile"
    - "docker-compose*.yml"

planner:
  max_parallel_tasks: 10
  algorithms:
    - genetic
    - simulated_annealing

executor:
  sandbox_enabled: true
  rollback_on_error: true
  max_cpu_percent: 50
  max_memory_mb: 1024

learning:
  metrics_db: data/metrics.db
  adaptation_interval_hours: 24
```

---

## 📊 Статус разработки

### Текущее состояние

| Компонент | Статус | Покрытие тестами | Примечание |
|-----------|--------|------------------|------------|
| **Project Scanner** | 🟡 MVP | ~40% | Базовый анализ Python/JS |
| **Task Planner** | 🟡 В разработке | ~30% | Генетические алгоритмы |
| **Executor** | 🔴 Planning | 0% | Sandbox, rollback |
| **Learning System** | 🔴 Planning | 0% | Метрики, адаптация |
| **Интеграции** | 🟡 Частично | ~20% | GitHub, Prometheus |

### Метрики

- **Health:** 🟢 OK (все сервисы доступны)
- **Tests:** ⚠️ 15 валидационных тестов (требуются функциональные)
- **Coverage:** ⚠️ ~30% (цель: ≥80%)
- **Documentation:** 🟡 Частично (требуется обновление)

---

## 🔗 Интеграции с экосистемой

CAA интегрируется с другими компонентами `Portfolio System Architect`:

```
┌─────────────────────┐
│  cognitive-agent    │ ← Автономное выполнение
└──────────┬──────────┘
           │ использует
           ▼
┌─────────────────────┐
│  decision-engine    │ ← RAG + reasoning для сложных решений
└─────────────────────┘

┌─────────────────────┐
│  portfolio-organizer│ ← Сбор доказательств компетенций
└─────────────────────┘

┌─────────────────────┐
│  it-compass         │ ← Методология системного мышления
└─────────────────────┘

┌─────────────────────┐
│  codeassistant/     │ ← Скиллы для анализа и безопасности
└─────────────────────┘
```

### Зависимости

- **src/** — общие библиотеки (health checks, async helpers, LLM configs)
- **codeassistant/skills/** — скиллы (caa-audit, security, it-compass)
- **monitoring/** — Prometheus/Grafana для метрик

---

## 📈 Дорожная карта

### Q2 2026 (Май-Июнь)
- [x] Базовая структура и конфигурации
- [ ] Реализация Project Scanner (Python, JavaScript)
- [ ] Task Planner с генетическими алгоритмами
- [ ] 10 интеграционных тестов
- [ ] Документация для сообщества (README-COMMUNITY.md)

### Q3 2026 (Июль-Сентябрь)
- [ ] Полный Executor с sandbox
- [ ] Learning System (сбор метрик)
- [ ] Интеграция с Jira/Slack
- [ ] Docker-образ для production

### Q4 2026 (Октябрь-Декабрь)
- [ ] Поддержка Go, Rust, Java
- [ ] Облачные интеграции (AWS/Azure)
- [ ] CLI-интерфейс с TUI
- [ ] Вынос в отдельный репозиторий (при готовности)

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

Смотрите [README-COMMUNITY.md](./README-COMMUNITY.md) — там подробное руководство по добавлению скиллов, интеграций и шаблонов.

---

## 📚 Документация

| Документ | Назначение |
|----------|------------|
| [README-COMMUNITY.md](./README-COMMUNITY.md) | Внешняя документация для сообщества |
| [IMPLEMENTATION_REPORT.md](./IMPLEMENTATION_REPORT.md) | Детальная реализация, архитектура |
| [USAGE.md](./USAGE.md) | Инструкции по запуску |
| `docs/` (в разработке) | Полная документация |

---

## ⚠️ Известные проблемы

См. [docs/KNOWN-TEST-ISSUES.md](../../docs/KNOWN-TEST-ISSUES.md) — документация пре-существующих проблем с тестами.

**Текущие issues:**
- 🔴 Интеграционные тесты требуют Docker-окружения
- 🟡 Покрытие тестами < 80% (цель: ≥80%)
- 🟡 Некоторые скиллы — заглушки (нет реальной реализации)

---

## 🛡️ Безопасность

- **Sandbox для команд:** все команды выполняются в изолированной среде
- **Лимиты ресурсов:** CPU ≤50%, память ≤1GB
- **Откат изменений:** автоматический rollback при ошибках
- **Аудит логов:** все действия агента логируются
- **Без секретов:** агент не хранит и не передает API-ключи

Подробнее: [`SECURITY.md`](../../SECURITY.md)

---

## 📄 Лицензия

MIT License — смотрите файл [`LICENSE`](../../LICENSE) для деталей.

---

## 📬 Контакты

- **Проблемы/Предложения:** [GitHub Issues](https://github.com/yourname/portfolio-system-architect/issues)
- **Обсуждение:** [GitHub Discussions](https://github.com/yourname/portfolio-system-architect/discussions)
- **Основной репозиторий:** [Portfolio System Architect](https://github.com/yourname/portfolio-system-architect)

---

**Часть экосистемы [Portfolio System Architect](../../README.md)**
*Made with ❤️ by the Community*
