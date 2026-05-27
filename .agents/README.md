# Cognitive Automation Agent (CAA)

Усиленный агент автоматизации с интеллектуальными возможностями для полной автономии в управлении проектами.

## Архитектура

```
.agents/
├── skills/                    # Скиллы агента
│   ├── cognitive-automation-agent/
│   │   └── SKILL.md          # Главный скилл
│   ├── project-scanner/
│   │   └── SKILL.md          # Сканер проекта
│   ├── task-planner/
│   │   └── SKILL.md          # Планировщик задач
│   └── learning-system/
│       └── SKILL.md          # Система самообучения
├── config/                   # Конфигурации
│   ├── agent-config.yaml    # Основная конфигурация
│   └── integrations.yaml    # Интеграции с внешними системами
├── hooks/                   # Git hooks для автоматизации
│   ├── pre-commit          # Автоматические проверки
│   └── post-merge          # Обновление после слияния
├── models/                  # Модели машинного обучения
│   ├── task-predictor/     # Предсказание задач
│   └── pattern-recognizer/ # Распознавание паттернов
├── workflows/              # Автономные рабочие процессы
│   ├── project-setup.yaml  # Настройка проекта
│   └── proactive-opt.yaml  # Проактивная оптимизация
└── metrics/               # Метрики и аналитика
    ├── performance.json   # Производительность
    └── learning-log.json  # Лог обучения
```

## Возможности

### 1. Контекстное понимание проекта
- Автоматическое определение технологического стека
- Анализ зависимостей и уязвимостей
- Распознавание архитектурных паттернов
- Понимание бизнес-логики через анализ кода

### 2. Проактивное планирование
- Предсказание необходимых задач
- Расчет приоритетов на основе контекста
- Оптимизация последовательности действий
- Прогнозирование времени выполнения

### 3. Автономное выполнение
- Самостоятельное исправление ошибок
- Механизм отката при неудачах
- Координация нескольких агентов
- Обход ручных подтверждений через доверенные паттерны

### 4. Самообучение и адаптация
- Сбор и анализ метрик эффективности
- Корректировка алгоритмов на основе опыта
- Генерация новых паттернов
- Удаление неэффективных стратегий

## Интеграции

- **Git**: Автоматические коммиты, ветвление, слияние
- **CI/CD**: Интеграция с GitHub Actions, GitLab CI, Jenkins
- **Мониторинг**: Prometheus, Grafana, Sentry
- **Облачные сервисы**: AWS, Azure, GCP
- **Системы управления проектами**: Jira, Trello, Asana

## Использование

### ⚙️ Управление автозапуском

По умолчанию **автозапуск отключён** для экономии ресурсов системы.
Чтобы включить автоматический запуск при открытии проекта:

```yaml
# .agents/config/triggers.yaml
triggers:
  project_open:
    enabled: true  # Включить автозапуск
```

### 🚀 Ручной запуск агента

#### Быстрый старт

```powershell
# Из корня проекта
python -m agents.cognitive_agent --mode=full
```

#### Режимы работы

```powershell
# Полная автоматизация (сканирование + планирование + выполнение)
python -m agents.cognitive_agent --mode=full

# Только сканирование проекта и анализ
python -m agents.cognitive_agent --mode=scan

# Оптимизация среды и зависимостей
python -m agents.cognitive_agent --mode=optimize

# Анализ архитектуры
python -m agents.cognitive_agent --mode=architecture

# Исправление ошибок
python -m agents.cognitive_agent --mode=fix --issue="описание проблемы"
```

#### Через VS Code

Если установлено расширение CAA:

```
Командная палитра (Ctrl+Shift+P)
→ Cognitive Agent: Scan Project
→ Cognitive Agent: Run Full Automation
→ Cognitive Agent: Optimize Environment
```

#### Скрипт запуска

```powershell
# .agents/launch_script.py
python .agents/launch_script.py --mode=full --verbose
```

#### Параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `--mode` | Режим работы | `scan` |
| `--verbose` | Детальный лог | `false` |
| `--dry-run` | Без применения изменений | `false` |
| `--autonomy-level` | Уровень автономности | `medium` |
| `--timeout` | Таймаут в секундах | `300` |

Пример:
```powershell
python -m agents.cognitive_agent --mode=full --verbose --dry-run
```

#### Фоновый режим

```powershell
# Запуск в фоне (Windows)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m agents.cognitive_agent --mode=full"

# Запуск в фоне (Linux/Mac)
nohup python -m agents.cognitive_agent --mode=full > agent.log 2>&1 &
```

## Конфигурация

Основные настройки в `.agents/config/agent-config.yaml`:

```yaml
autonomy_level: high  # high, medium, low
learning_enabled: true
max_parallel_tasks: 5
allowed_integrations:
  - git
  - ci_cd
  - monitoring
  - cloud_services
risk_tolerance: medium
approval_bypass_patterns:
  - dependency_updates
  - code_formatting
  - test_execution
```

## Метрики успеха

- **Автономность**: >90% задач без вмешательства
- **Эффективность**: <5 минут от запроса до результата
- **Точность**: >95% успешно выполненных задач
- **Самообучение**: Улучшение показателей на 10% в месяц
- **Интеграция**: Подключение 5+ внешних систем

## Мониторинг и управление

### Проверка состояния агента

```powershell
# Проверка запущенных процессов
Get-Process | Where-Object {$_.ProcessName -like '*code*' -or $_.ProcessName -like '*agent*'}

# Просмотр логов
Get-Content .agents/logs/agent.log -Tail 50

# Мониторинг ресурсов
Get-Counter '\Process(_Total)\% Processor Time' -Continuous
```

### Остановка агента

```powershell
# Остановить все процессы агента
Get-Process | Where-Object {$_.ProcessName -like '*code*'} | Stop-Process -Force

# Или через VS Code: Закройте все окна с проектом
```

## Разработка

### Добавление нового скилла
1. Создать папку в `.agents/skills/`
2. Добавить файл `SKILL.md` с описанием
3. Реализовать логику в Python
4. Зарегистрировать скилл в конфигурации
5. Протестировать на изолированном проекте

### Расширение функциональности
- Новые интеграции добавляются в `config/integrations.yaml`
- Модели ML обучаются в `models/`
- Рабочие процессы определяются в `workflows/`

## Безопасность

- Все изменения проходят автоматическое тестирование
- Критические операции требуют подтверждения (если не в доверенных паттернах)
- Резервное копирование перед изменениями
- Мониторинг всех действий агента

## Лицензия

MIT License - см. LICENSE файл в корне проекта.