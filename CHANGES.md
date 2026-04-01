# Изменения для инструмента repo-audit

## Добавленные файлы

1. **Документация:**
   - `docs/repo-audit-plan.md` — план и архитектура инструмента
   - `docs/audit-workflow.md` — описание workflow и интеграций
   - `docs/ai-skill-sourcecraft.md` — конфигурация AI-навыка
   - `docs/audit-testing-plan.md` — план тестирования
   - `docs/repo-audit-deployment.md` — инструкции по установке и использованию

2. **Конфигурация:**
   - `.github/workflows/repo-audit.yml` — GitHub Actions workflow для автоматического аудита
   - `.sourcecraft/skills/repo-audit-assistant.yml` — конфиг AI-навыка для SourceCraft
   - `.repo-audit.yaml` — пример конфигурации проверок

3. **Исходный код (заглушки для реализации):**
   - `src/repo_audit/__init__.py`
   - `src/repo_audit/cli.py`
   - `src/repo_audit/checker.py`
   - `src/repo_audit/checks/`
   - `src/repo_audit/report.py`
   - `src/repo_audit/config.py`
   - `tests/`

## Изменения в существующих файлах

1. **README.md** — добавлен раздел "Automated Repository Audit"
2. **pyproject.toml** — добавлена зависимость `repo-audit` (после публикации)
3. **requirements-dev.txt** — добавлены dev-зависимости для тестирования

## Коммит-сообщение

```
feat: add repo-audit tool for automated repository maturity checks

- Add comprehensive documentation for repo-audit tool
- Implement GitHub Actions workflow for automatic auditing
- Create AI skill configuration for SourceCraft integration
- Prepare source code structure for future implementation
- Update project configuration and dependencies
```

## Следующие шаги

1. Создать PR с этими изменениями.
2. Зарегистрировать AI-навык в SourceCraft.
3. Запустить инструмент на текущем репозитории для проверки.
4. Итеративно улучшать проверки на основе результатов.
