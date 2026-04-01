# Интеграция аудита репозитория с GitHub Actions

## Обзор
GitHub Actions workflow будет запускать инструмент аудита при каждом пуше в ветки `main`/`develop` и при создании Pull Request. Результаты будут доступны как артефакт и, опционально, как комментарий в PR.

## Workflow файл

Создадим `.github/workflows/repo-audit.yml`:

```yaml
name: Repository Audit
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # для полной истории git

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install repo-audit tool
        run: |
          pip install -e ./tools/repo-audit
          # или из PyPI, когда будет опубликовано
          # pip install repo-audit

      - name: Run audit for all levels
        id: audit
        run: |
          python -m repo_audit run \
            --level all \
            --format markdown \
            --output audit-report.md \
            --fail-on-required

      - name: Upload audit report as artifact
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit-report.md

      - name: Comment PR (if applicable)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('audit-report.md', 'utf8');
            const { issue: { number } } = context;
            const { owner, repo } = context.repo;
            await github.rest.issues.createComment({
              owner,
              repo,
              issue_number: number,
              body: `## 📋 Отчёт аудита репозитория\n\n${report}`
            });
```

## Расширенный workflow с оценкой

Можно добавить оценку (score) на основе пройденных проверок и установить статус проверки (pass/fail).

```yaml
      - name: Calculate score
        run: |
          python -m repo_audit score --output score.json
          SCORE=$(jq '.score' score.json)
          echo "SCORE=$SCORE" >> $GITHUB_ENV

      - name: Fail if score below threshold
        if: env.SCORE < 70
        run: |
          echo "Score $SCORE is below 70. Failing workflow."
          exit 1
```

## Планируемые улучшения

1. **Кэширование** — кэшировать виртуальное окружение Python для ускорения.
2. **Параллельные проверки** — запускать проверки разных уровней параллельно.
3. **Визуализация** — генерировать badge (щиток) с оценкой зрелости репозитория.
4. **Уведомления** — отправлять результаты в Slack/Telegram при деградации.

## Интеграция с существующими workflows

Аудит можно добавить как дополнительный шаг в уже существующие CI-пайплайны (например, после тестов).

Пример добавления в `ci.yml`:

```yaml
      - name: Run repository audit
        if: always()
        run: |
          pip install repo-audit
          python -m repo_audit run --level level1,level2 --format json
```

## Переменные окружения

- `REPO_AUDIT_CONFIG` — путь к кастомному чек-листу YAML (по умолчанию `checklist.yaml`).
- `REPO_AUDIT_OUTPUT_FORMAT` — формат вывода (json, markdown, html).
- `REPO_AUDIT_FAIL_ON_REQUIRED` — флаг для завершения с ошибкой, если обязательные проверки не пройдены.

## Пример чек-листа

Создадим `checklist.yaml` в корне репозитория или в `.github/audit/checklist.yaml`.

## Следующие шаги

1. Реализовать инструмент `repo-audit` с поддержкой CLI.
2. Протестировать workflow локально с помощью `act`.
3. Запушить workflow в репозиторий и убедиться, что он работает.
4. Добавить badge в README.
