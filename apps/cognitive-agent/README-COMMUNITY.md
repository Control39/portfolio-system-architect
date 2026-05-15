# 🤖 Cognitive Automation Agent

> **Автономный ИИ-агент для настройки и управления проектами**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-coming%20soon-green.svg)](https://github.com/yourname/cognitive-agent/tests)
[![Status](https://img.shields.io/badge/status-MVP-orange.svg)](https://github.com/yourname/cognitive-agent/issues)

## 🎯 Что это?

**Cognitive Automation Agent (CAA)** — автономный ИИ-агент, который:
- 📊 **Анализирует** проекты: определяет стек, зависимости, архитектурные паттерны
- 📋 **Планирует задачи**: предсказывает, что нужно сделать, до явного запроса
- ⚡ **Выполняет работу**: настраивает окружение, создает файлы, запускает команды
- 🧠 **Самообучается**: улучшает алгоритмы на основе метрик эффективности

**Пример использования:** Открываете новый проект → агент за 2 минуты настраивает Docker, CI/CD, линтеры → вы начинаете кодить.

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/yourname/cognitive-agent.git
cd cognitive-agent

# Установить зависимости
pip install -r requirements.txt

# Или через pip (когда будет на PyPI)
pip install cognitive-agent
```

### Запуск (демо-режим)

```bash
# Анализ проекта в текущей директории
python -m cognitive_agent scan .

# Автоматическая настройка нового проекта
python -m cognitive_agent setup --template=fastapi

# Запуск в режиме наблюдения (мониторинг изменений)
python -m cognitive_agent watch .
```

### Пример: Настройка FastAPI-проекта за 5 минут

```bash
# 1. Создаем пустую папку
mkdir my-fastapi-app && cd my-fastapi-app

# 2. Запускаем агента
cognitive-agent setup --template=fastapi

# Агент автоматически:
# ✅ Создает структуру проекта (src/, tests/, docs/)
# ✅ Генерирует requirements.txt с зависимостями
# ✅ Настраивает docker-compose.yml (PostgreSQL + Redis)
# ✅ Создает GitHub Actions workflow для CI/CD
# ✅ Добавляет pre-commit hooks (black, ruff, mypy)
# ✅ Пишет базовый README.md

# 3. Начинаете кодить
code .
```

---

## 📦 Возможности

### 🔍 Project Scanner
- **Автоматическое определение стека:** Python, JavaScript, Go, Rust и др.
- **Анализ зависимостей:** `requirements.txt`, `package.json`, `Cargo.toml`
- **Распознавание паттернов:** MVC, микросервисы, event-driven
- **Поиск уязвимостей:** устаревшие пакеты, небезопасные конфигурации

### 📋 Task Planner
- **Интеллектуальная приоритизация:** срочность, важность, зависимости
- **Оптимизация последовательности:** группировка для параллельного выполнения
- **Адаптивное планирование:** корректировка на основе метрик выполнения
- **Поддержка сценариев:** project-setup, code-review, performance-optimization

### ⚡ Autonomous Executor
- **Безопасное выполнение:** sandbox для команд, лимиты ресурсов
- **Откат изменений:** автоматический rollback при ошибках
- **Уровни автономности:**
  - `high` — без подтверждения (доверенные паттерны)
  - `medium` — подтверждение для критичных операций
  - `low` — только рекомендации

### 🧠 Learning System
- **Сбор метрик:** время выполнения, успешность, потребление ресурсов
- **Анализ эффективности:** какие стратегии работают лучше
- **Адаптация алгоритмов:** автоматическая настройка параметров
- **Прогнозирование:** предсказание успешности задач

---

## 🏗️ Архитектура

```
cognitive-agent/
├── src/
│   ├── scanner/           # Project Scanner (анализ стека)
│   │   ├── python_scanner.py
│   │   ├── javascript_scanner.py
│   │   └── architecture_detector.py
│   ├── planner/           # Task Planner (планирование)
│   │   ├── priority_engine.py
│   │   ├── optimizer.py
│   │   └── workflow_runner.py
│   ├── executor/          # Autonomous Executor (выполнение)
│   │   ├── command_runner.py
│   │   ├── sandbox.py
│   │   └── rollback_manager.py
│   ├── learning/          # Learning System (самообучение)
│   │   ├── metrics_collector.py
│   │   ├── analyzer.py
│   │   └── adapter.py
│   └── core/              # Ядро агента
│       ├── agent.py
│       ├── config.py
│       └── logger.py
├── workflows/             # Готовые сценарии
│   ├── project-setup.yaml
│   ├── code-review.yaml
│   └── performance-opt.yaml
├── templates/             # Шаблоны проектов
│   ├── fastapi/
│   ├── flask/
│   ├── django/
│   └── react/
├── tests/                 # Тесты
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/                # Конфигурации
│   ├── agent-config.yaml
│   └── trusted-patterns.yaml
└── docs/                  # Документация
```

### Ключевые компоненты

| Компонент | Назначение | Статус |
|-----------|------------|--------|
| **Project Scanner** | Анализ проекта, определение стека | 🟢 MVP |
| **Task Planner** | Планирование и приоритизация | 🟡 В разработке |
| **Executor** | Безопасное выполнение команд | 🟡 В разработке |
| **Learning System** | Сбор метрик и адаптация | 🔴 Планируется |

---

## 🔧 Конфигурация

### Базовая настройка

Создайте `~/.cognitive-agent/config.yaml`:

```yaml
agent:
  autonomy_level: medium  # high, medium, low
  max_parallel_tasks: 5
  timeout_seconds: 3600

scanner:
  enabled_languages:
    - python
    - javascript
    - go
  max_depth: 10

planner:
  algorithms:
    - genetic
    - simulated_annealing
  priority_factors:
    - urgency: 0.4
    - importance: 0.4
    - complexity: 0.2

executor:
  sandbox_enabled: true
  max_cpu_percent: 50
  max_memory_mb: 1024
  rollback_on_error: true

learning:
  metrics_db: ~/.cognitive-agent/metrics.db
  adaptation_interval_hours: 24
```

### Доверенные паттерны

Для `autonomy_level: high` настройте паттерны, которые выполняются без подтверждения:

```yaml
trusted_patterns:
  - "requirements*.txt"
  - ".github/workflows/*"
  - "Dockerfile"
  - "docker-compose*.yml"
  - "*.test.*"
  - "pre-commit-config.yaml"
```

---

## 📊 Интеграции

### Поддерживаемые системы

| Система | Статус | Описание |
|---------|--------|----------|
| **GitHub** | 🟢 | Анализ репозиториев, создание PR |
| **GitLab** | 🟡 | Частичная поддержка |
| **Jira** | 🔴 | В планах |
| **Slack/Telegram** | 🟡 | Уведомления |
| **Prometheus/Grafana** | 🟢 | Мониторинг метрик |
| **Docker** | 🟢 | Управление контейнерами |

### Пример интеграции с GitHub

```python
from cognitive_agent.integrations import GitHubIntegration

gh = GitHubIntegration(token="your_token")
repo = gh.scan_repo("owner/repo-name")

# Агент проанализирует репозиторий
print(f"Стек: {repo.technology_stack}")
print(f"Зависимости: {repo.dependencies}")
print(f"Архитектурные паттерны: {repo.architecture_patterns}")

# Сгенерировать план улучшений
plan = repo.generate_improvement_plan()
for task in plan.tasks:
    print(f"- {task.description} (приоритет: {task.priority})")
```

---

## 🧪 Тестирование

```bash
# Юнит-тесты
pytest tests/unit/ -v

# Интеграционные тесты
pytest tests/integration/ -v

# E2E тесты (требуют Docker)
pytest tests/e2e/ -v --docker

# Покрытие кода
pytest --cov=src --cov-report=html
```

---

## 🤝 Вклад в проект

Мы приветствуем вклад сообщества! Вот как вы можете помочь:

### Новые скиллы (skills)
Добавьте поддержку новых технологий:
- [ ] Go модули (`go.mod`)
- [ ] Rust crates (`Cargo.toml`)
- [ ] Java Maven/Gradle
- [ ] TypeScript проекты

### Интеграции
Подключите внешние системы:
- [ ] Jira/Asana для управления задачами
- [ ] Notion для документации
- [ ] AWS/Azure/GCP для облачных развертываний

### Шаблоны проектов
Создайте шаблоны для популярных стеков:
- [ ] FastAPI + PostgreSQL + Redis
- [ ] Django + Celery + RabbitMQ
- [ ] React + Node.js + MongoDB

### Как внести вклад
1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Пушните ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

**Правила:**
- Все функции должны иметь тесты
- Код должен проходить линтинг (`ruff check .`)
- Документация должна быть обновлена

---

## 📈 Дорожная карта

### Q2 2026 (Май-Июнь)
- [x] Базовый Project Scanner (Python, JavaScript)
- [ ] Task Planner с генетическими алгоритмами
- [ ] 10 интеграционных тестов
- [ ] Документация для сообщества

### Q3 2026 (Июль-Сентябрь)
- [ ] Полный Executor с sandbox
- [ ] Learning System (сбор метрик)
- [ ] Интеграция с Jira/Slack
- [ ] Docker-образ для production

### Q4 2026 (Октябрь-Декабрь)
- [ ] Поддержка Go, Rust, Java
- [ ] Облачные интеграции (AWS/Azure)
- [ ] CLI-интерфейс с TUI
- [ ] PyPI релиз v1.0

---

## 📚 Документация

- [Быстрый старт](docs/quickstart.md) — настройка за 5 минут
- [Архитектура](docs/architecture.md) — детальное описание компонентов
- [Руководство по вкладу](docs/contributing.md) — как добавить свой скилл
- [API Reference](docs/api.md) — документация для разработчиков
- [Частые вопросы](docs/faq.md) — ответы на популярные вопросы

---

## 🛡️ Безопасность

- **Sandbox для команд:** все команды выполняются в изолированной среде
- **Лимиты ресурсов:** CPU, память, время выполнения
- **Откат изменений:** автоматический rollback при ошибках
- **Аудит логов:** все действия агента логируются
- **Без секртов:** агент не хранит и не передает API-ключи

Подробнее: [SECURITY.md](SECURITY.md)

---

## 📄 Лицензия

MIT License — смотрите файл [LICENSE](LICENSE) для деталей.

---

## 🙏 Благодарности

Этот проект создан как часть экосистемы [Portfolio System Architect](https://github.com/yourname/portfolio-system-architect) — демонстрации когнитивной архитектуры и системного мышления.

Спасибо сообществу за вдохновение и поддержку!

---

## 📬 Контакты

- **Проблемы/Предложения:** [GitHub Issues](https://github.com/yourname/cognitive-agent/issues)
- **Обсуждение:** [GitHub Discussions](https://github.com/yourname/cognitive-agent/discussions)
- **Автор:** [Ваше имя/никнейм]
- **Основной репозиторий:** [Portfolio System Architect](https://github.com/yourname/portfolio-system-architect)

---

**Made with ❤️ by the Community**
