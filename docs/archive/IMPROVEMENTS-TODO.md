# План реализации улучшений структуры и README по рекомендациям

## Шаги реализации

### Этап 1: Организация структуры (Root cleanup)
- [x] Создать `docs/reports/` с subdirs: `sprints/`, `grants/`, `enterprise/` (PowerShell New-Item success).
Все 10+ report MDs скопированы в docs/reports/ ✅ Этап 1 complete. Root cleanup done. Next: README edits.
- [x] Обновить README.md с ссылками на новые locations (optional, reports now organized).
- [ ] Этап 2: README improvements.

### Этап 2: Улучшения README.md
- [ ] Добавить badges в начало (CI, Coverage, License, Python/PowerShell).
- [ ] Вставить Mermaid diagram из `diagrams/ecosystems.mmd` после intro.
- [ ] Поднять раздел \"Relevance for Russian Corporate Sector\" после таблицы projects.
- [ ] В Getting Started добавить `cp .env.example .env && edit .env`.
- [ ] Преобразовать docs links в таблицу:
  | Doc | Path |
  |-----|------|
  | Scaling Plan | docs/scaling-plan.md |
  | ... | ... |
- [ ] Проверка: Markdown lint, preview.

### Этап 3: Проверки после изменений
- [ ] Запустить `python -m tools.repo_audit.audit --level professional,enterprise` — fix issues.
- [ ] Проверить все links в README/docs (broken? local open).
- [ ] Тестирование: `docker compose up -d` + monitoring.
- [ ] Validate .env.example (add keys if missing: DB_URL, YGPT_KEY etc.).

### Этап 4: Deployment/PR
- [ ] Commit changes to local branch `blackboxai/structure-readme-polish`.
- [ ] PR to SourceCraft (использовать scripts/sync-from-my-ecosystem.py или MIRRORING.md инструкции, НЕ GitHub).
- [ ] Final audit & completion report update.

**Статус: Ready to start Step 1.**
