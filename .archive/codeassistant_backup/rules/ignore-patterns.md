# Правила исключения для ИИ-агентов

## 🚫 Игнорировать (не индексировать, не анализировать)

### Системные / кэш
- `.venv/**` — виртуальное окружение Python
- `__pycache__/**`, `*.pyc`, `*.pyo` — кэш компиляции
- `.mypy_cache/**`, `.pytest_cache/**` — кэш инструментов
- `.cache/**`, `cache/**` — общий кэш
- `node_modules/**` — зависимости Node.js
- `.git/**` — история Git (агенты читают только текущий код)

### Авто-генерация / отчёты
- `badges/**`, `*-report.json`, `*-report.txt` — авто-отчёты, пересоздаются
- `ecosystem-analysis-report.*`, `project_health_report.json` — метрики
- `test_reports/**`, `reports/` (кроме `docs/reports/`) — результаты прогонов

### Личные / рабочие файлы
- `my-repo-map.csv`, `my-repo-map-full.csv`, `my-repo-map-simple.txt` — личные заметки
- `settings/mcp_settings.json` — локальные настройки инструментов
- `tasks/019d*/` — временные задачи с выводом команд
- `source` — артефакты, не часть архитектуры

### Документация-дубликаты
- `docs/archive/**` — архив, не актуально для анализа
- `docs/docs/history/journey/0*_*/` — перенесено в `.codeassistant/context.md`

## ✅ Приоритет для анализа (где искать архитектуру)

### Ядро проекта
- `apps/*/src/**` — исходный код компонентов
- `apps/arch-compass-framework/src/core/contracts/**` — интерфейсы (`IAiProvider`, `IModule`)
- `apps/arch-compass-framework/src/core/diagnostics/**` — само-аудит, метрики
- `src/core/**` — общие утилиты, валидация, логирование

### Документация
- `README.md`, `apps/*/README.md` — описание компонентов
- `docs/architecture/decisions/**` — ADR
- `docs/methodology/**` — методология IT-Compass
- `.codeassistant/context.md` — контекст для ассистента

### Конфигурация
- `.vscode/settings.json` — правила для редактора
- `Dockerfile`, `docker-compose.yml` — сборка и деплой
- `.github/workflows/*.yml` — CI/CD пайплайны
