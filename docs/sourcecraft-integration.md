# Интеграция с SourceCraft

## Создание issue в SourceCraft

### Шаблон issue

**Title:** Integrate repo-audit tool into portfolio-system-architect

**Description:**
We have developed a comprehensive repository audit tool (`repo-audit`) that automatically checks repository maturity across three levels (Base, Professional, Enterprise). The tool includes:

- Python CLI with plugin-based checks
- GitHub Actions workflow for automatic auditing
- AI skill for SourceCraft that provides recommendations
- Detailed reporting in multiple formats (JSON, Markdown, HTML)

**Tasks:**
1. Register the AI skill in SourceCraft using `.sourcecraft/skills/repo-audit-assistant.yml`
2. Create a new project "Repository Maturity" in SourceCraft
3. Add labels: `repo-audit`, `automation`, `ci-cd`, `security`, `documentation`
4. Configure webhook from GitHub to trigger AI skill on PR events
5. Test the integration by creating a test PR and verifying AI comments

**Acceptance Criteria:**
- AI skill responds to `/audit` command in SourceCraft chat
- GitHub PRs receive automatic audit comments
- Audit reports are stored as artifacts in GitHub Actions
- All checks pass for Level 1 (Base) on the main branch

## Добавление лейблов

Используйте SourceCraft API или UI для добавления следующих лейблов:

```yaml
labels:
  - name: repo-audit
    color: "#00FF00"
    description: "Related to repository audit tool"
  - name: automation
    color: "#FF9900"
    description: "Automation of development processes"
  - name: ci-cd
    color: "#3366FF"
    description: "Continuous integration and deployment"
  - name: security
    color: "#FF0000"
    description: "Security-related checks and fixes"
  - name: documentation
    color: "#6600CC"
    description: "Documentation improvements"
```

## Регистрация AI-навыка

### Через CLI SourceCraft

```bash
# Установите SourceCraft CLI если ещё не установлен
npm install -g @sourcecraft/cli

# Авторизуйтесь
sourcecraft login

# Зарегистрируйте навык
sourcecraft skill register .sourcecraft/skills/repo-audit-assistant.yml

# Проверьте статус
sourcecraft skill list
```

### Через UI SourceCraft

1. Откройте SourceCraft Dashboard
2. Перейдите в раздел "AI Skills"
3. Нажмите "Add New Skill"
4. Загрузите YAML-конфиг из `.sourcecraft/skills/repo-audit-assistant.yml`
5. Сохраните и активируйте навык

## Конфигурация вебхука

### GitHub → SourceCraft

1. В настройках репозитория GitHub перейдите в "Webhooks"
2. Добавьте новый вебхук:
   - Payload URL: `https://api.sourcecraft.ai/webhook/github`
   - Content type: `application/json`
   - Secret: (используйте секрет из SourceCraft)
   - Events: "Pull requests" и "Push"
3. Сохраните вебхук

### SourceCraft → GitHub

1. В SourceCraft Dashboard перейдите в "Integrations" → "GitHub"
2. Подключите репозиторий `portfolio-system-architect`
3. Настройте автоматическое создание комментариев в PR

## Тестирование интеграции

### Шаг 1: Создание тестового PR

```bash
git checkout -b test-audit
# Внесите минимальные изменения
git commit -m "test: add test file for audit"
git push origin test-audit
# Создайте PR через GitHub UI
```

### Шаг 2: Проверка AI-комментария

1. Откройте созданный PR
2. Дождитесь завершения GitHub Actions workflow
3. Проверьте, что AI-навык оставил комментарий с отчётом аудита

### Шаг 3: Проверка команды в чате

1. Откройте SourceCraft чат
2. Введите: `/audit repo portfolio-system-architect level 2`
3. Убедитесь, что получен подробный отчёт

## Устранение неполадок

### Проблема: AI-навык не отвечает

- Проверьте статус навыка: `sourcecraft skill status repo-audit-assistant`
- Проверьте логи: `sourcecraft logs --skill repo-audit-assistant`
- Убедитесь, что вебхук правильно настроен

### Проблема: GitHub Actions не запускается

- Проверьте наличие файла `.github/workflows/repo-audit.yml`
- Убедитесь, что workflow имеет правильные триггеры
- Проверьте логи GitHub Actions

### Проблема: Нет доступа к SourceCraft API

- Проверьте API-токен: `sourcecraft config get api_token`
- Обновите токен при необходимости: `sourcecraft login --refresh`

## Дальнейшие шаги

После успешной интеграции:

1. Добавьте мониторинг использования навыка (метрики в Prometheus)
2. Настройте автоматическое создание issue при обнаружении критических нарушений
3. Расширьте набор проверок на основе обратной связи
4. Опубликуйте инструмент как open-source проект