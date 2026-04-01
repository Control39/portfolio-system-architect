# Развёртывание и документация инструмента repo-audit

## Установка

### Вариант 1: Установка из PyPI (рекомендуется)

```bash
pip install repo-audit
```

### Вариант 2: Установка из исходников

```bash
git clone https://github.com/your-org/repo-audit.git
cd repo-audit
pip install -e .
```

### Вариант 3: Использование Docker

```bash
docker pull ghcr.io/your-org/repo-audit:latest
docker run -v $(pwd):/repo ghcr.io/your-org/repo-audit run --level all
```

## Использование

### Базовые команды

```bash
# Запуск аудита всех уровней
repo-audit run --level all

# Аудит только уровня 1
repo-audit run --level 1

# Вывод в формате JSON
repo-audit run --format json

# Сохранение отчёта в файл
repo-audit run --output audit-report.md

# Показать справку
repo-audit --help
```

### Конфигурация

Создайте файл `.repo-audit.yaml` в корне репозитория для кастомизации проверок:

```yaml
checks:
  required_files:
    enabled: true
    files:
      - README.md
      - LICENSE
      - .gitignore
  branch_protection:
    enabled: true
    required_reviewers: 1
  code_coverage:
    enabled: true
    threshold: 80
```

## Интеграция с GitHub Actions

Добавьте в ваш workflow:

```yaml
name: Repository Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-org/repo-audit-action@v1
        with:
          level: all
          format: markdown
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit-report.md
```

## AI-навык для SourceCraft

### Установка навыка

1. Скопируйте конфиг `.sourcecraft/skills/repo-audit-assistant.yml` в ваш репозиторий.
2. Зарегистрируйте навык в SourceCraft:

```bash
sourcecraft skill register .sourcecraft/skills/repo-audit-assistant.yml
```

### Использование навыка

- В чате SourceCraft: `/audit repo`
- По событию PR: навык автоматически прокомментирует отчёт аудита.
- По команде: `audit level 2`

## Мониторинг и метрики

Инструмент может экспортировать метрики в Prometheus:

```bash
repo-audit run --export-metrics metrics.prom
```

Пример дашборда Grafana включён в `monitoring/grafana/dashboards/repo-audit.json`.

## Обновление

Для обновления до последней версии:

```bash
pip install --upgrade repo-audit
```

## Устранение неполадок

### Ошибка "Check failed"

Если какая-то проверка не проходит, инструмент вернёт ненулевой код выхода и детали в логах. Используйте `--verbose` для подробного вывода.

### Ошибка интеграции с GitHub

Убедитесь, что токен GitHub имеет права на чтение репозитория и проверку branch protection.

### Ошибка AI-навыка

Проверьте, что инструмент `repo-audit` установлен в окружении, где работает SourceCraft.

## Лицензия

Инструмент распространяется под лицензией MIT. Подробности в файле `LICENSE`.

## Вклад в разработку

Мы приветствуем пул-реквесты! Пожалуйста, ознакомьтесь с `CONTRIBUTING.md`.

## Поддержка

- Документация: https://repo-audit.readthedocs.io/
- Issues: https://github.com/your-org/repo-audit/issues
- Чат: Slack #repo-audit

## Благодарности

Спасибо сообществу за идеи и обратную связь. Особенно участникам обсуждения чек-листов зрелости репозиториев.
