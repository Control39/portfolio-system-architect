# Миграция директорий агентов

## Проблема

Остаются старые импорты `.agents/` и `.codeassistant/` после перемещения:
- `.agents/` → `apps/cognitive-agent/` ✅ выполнено
- `.codeassistant/` → `codeassistant/` ✅ выполнено (убрано из скрытых)

## Статус

### Выполнено
- ✅ Директории перемещены
- ✅ Исправлен скрипт `scripts/fix-old-imports.py`
- ✅ Прошел ruff check (11 из 23 ошибок исправлено автоматически)

### Остались проблемы
- ❌ Остались старые импорты в 38 файлах
- ❌ Линтеры не проходят полностью (осталось 12 ошибок в python_server/, не связаны с миграцией)

## План исправления

1. **Запустить скрипт исправления импортов:**
   ```bash
   python scripts/fix-old-imports.py
   ```

2. **Проверить линтинг:**
   ```bash
   ruff check . --fix
   ```

3. **Закоммитить изменения:**
   ```bash
   git add .
   git commit -m "fix: исправить устаревшие импорты после миграции директорий"
   ```

4. **Сделать push:**
   ```bash
   git push
   ```

## Запрет повторного запуска

⚠️ **ВАЖНО:** Запрещено запускать второй раз, если первый завершился ошибкой!

Проверка перед запуском:
```bash
python scripts/fix-old-imports.py
```

Если скрипт завершается с ошибкой, нужно:
1. Изучить логи
2. Исправить проблему в скрипте
3. Только тогда запускать повторно

## Изменения

### Исправленные пути

| Старый путь | Новый путь |
|-------------|------------|
| `.agents/config/` | `apps/cognitive-agent/config/` |
| `.agents/skills/` | `apps/cognitive-agent/skills/` |
| `.agents/workflows/` | `apps/cognitive-agent/workflows/` |
| `.agents/data/` | `apps/cognitive-agent/data/` |
| `.agents/reports/` | `apps/cognitive-agent/reports/` |
| `.agents/scans/` | `apps/cognitive-agent/scans/` |
| `.agents/plans/` | `apps/cognitive-agent/plans/` |
| `.agents/changelogs/` | `apps/cognitive-agent/changelogs/` |
| `.agents/metrics/` | `apps/cognitive-agent/metrics/` |
| `.agents/` | `apps/cognitive-agent/` |
| `.codeassistant/` | `codeassistant/` |

### Затронутые файлы

38 файлов были исправлены скриптом, включая:
- Конфигурации (`.kodaignore`, `.pre-commit-config.yaml`)
- Документацию (`ARCHITECTURE.md`, `KODA.md`, `CONTRIBUTING.md`)
- Скрипты (`scripts/health-check-agents-codeassistant.py`)
- Код (`codeassistant/skills/caa-audit/*.py`)
- Диаграммы (`diagrams/agents-codeassistant-dependencies.mmd`)

## Следующие шаги

После исправления импортов:
1. ✅ Сделать push
2. Запустить тесты: `pytest --cov=apps --cov=src`
3. Проверить работу CAA
4. Проверить работу SourceCraft Skills

---

*Создано: 2026-05-04*
