# План реализации инструмента автоматической проверки репозитория

## Цель
Создать CLI-инструмент на Python, который проверяет репозиторий по чек-листу зрелости (три уровня + релизный) и генерирует отчёт.

## Архитектура

### Модули
1. **repo_audit.cli** — точка входа, парсинг аргументов.
2. **repo_audit.checker** — базовый класс проверки и регистр проверок.
3. **repo_audit.checks** — набор конкретных проверок, сгруппированных по уровням.
4. **repo_audit.report** — генерация отчётов (JSON, Markdown, HTML).
5. **repo_audit.config** — загрузка конфигурации (чек-лист YAML).

### Структура файлов
```
tools/repo-audit/
├── __init__.py
├── cli.py
├── checker.py
├── checks/
│   ├── __init__.py
│   ├── base.py
│   ├── level1_structure.py
│   ├── level2_professional.py
│   ├── level3_enterprise.py
│   └── release_checklist.py
├── report.py
├── config.py
└── checklist.yaml (шаблон чек-листа)
```

## Чек-лист в YAML

Файл `checklist.yaml` будет содержать все проверки с метаданными:

```yaml
version: 1.0
levels:
  - id: level1
    name: База (обязательный минимум)
    checks:
      - id: repo_structure
        description: Корневая структура соответствует шаблону
        command: python -m repo_audit.checks.level1_structure check_structure
        severity: required
      - id: required_files
        description: Наличие обязательных файлов (README, LICENSE, .gitignore и т.д.)
        command: ...
  - id: level2
    name: Профессиональный
    checks: [...]
  - id: level3
    name: Enterprise
    checks: [...]
  - id: release
    name: Релизный чек-лист
    checks: [...]
```

## Реализация проверок

Каждая проверка — это класс, наследующий от `BaseCheck`, реализующий метод `run() -> CheckResult`.

Пример:

```python
class RequiredFilesCheck(BaseCheck):
    def run(self, context: AuditContext) -> CheckResult:
        missing = []
        for f in ['README.md', 'LICENSE', '.gitignore']:
            if not os.path.exists(os.path.join(context.repo_root, f)):
                missing.append(f)
        if missing:
            return CheckResult(
                passed=False,
                message=f"Отсутствуют обязательные файлы: {missing}",
                details={"missing": missing}
            )
        return CheckResult(passed=True, message="Все обязательные файлы присутствуют.")
```

## Контекст проверки

`AuditContext` содержит:
- `repo_root` — путь к корню репозитория
- `config` — загруженный чек-лист
- `git_info` — информация о ветке, коммитах и т.д.

## CLI

Интерфейс командной строки:

```bash
python -m repo_audit run --level all --output report.json
python -m repo_audit run --level level1 --format markdown
python -m repo_audit list-checks
```

## Интеграция с GitHub Actions

Workflow будет запускать инструмент при каждом PR и комментировать результат.

Пример `.github/workflows/audit.yml`:

```yaml
name: Repository Audit
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run repo audit
        run: |
          pip install -e ./tools/repo-audit
          python -m repo_audit run --level all --format markdown --output audit.md
      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit.md
```

## AI-навык для SourceCraft

Навык будет использовать этот инструмент для анализа репозитория и предоставления рекомендаций.

Промт для навыка:
```
Ты — эксперт по качеству репозиториев. Проанализируй отчёт аудита и предложи конкретные шаги для улучшения.
```

## Следующие шаги

1. Переключиться в режим Code для реализации Python-кода.
2. Создать структуру модуля `tools/repo-audit`.
3. Реализовать базовые классы и 5–10 проверок уровня 1.
4. Написать тесты с pytest.
5. Интегрировать в GitHub Actions.
6. Создать AI-навык в SourceCraft.
7. Документировать и выпустить версию 0.1.0.
```

## Вопросы для уточнения

- Какой формат вывода предпочтительнее: JSON, Markdown, HTML?
- Нужна ли поддержка плагинов для пользовательских проверок?
- Следует ли интегрировать с существующими инструментами (например, repolinter)?
