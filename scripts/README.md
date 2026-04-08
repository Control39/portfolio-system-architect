# Scripts Directory Structure

This directory contains utility scripts for development, deployment, and maintenance of the portfolio system. The scripts are organized by platform and purpose to demonstrate cross-platform expertise.

## 🏗️ Structure Rationale

The mixed scripting approach (PowerShell, Bash, Python, Batch) is **intentional** and demonstrates:

1. **Cross-platform expertise** – ability to work in both Windows and Linux environments
2. **Pragmatic tool selection** – using the right tool for each specific task
3. **Enterprise relevance** – many Russian companies use mixed environments
4. **Automation versatility** – scripts for CI/CD, local development, and production

## 📁 Directory Organization

### `windows/` – Windows-specific scripts
- **Purpose**: Scripts that require Windows-specific features or are meant to run in Windows environments
- **Languages**: PowerShell (.ps1), Batch (.bat)
- **Examples**: 
  - `fix_encoding.ps1` – fixes file encoding issues (Windows-specific)
  - `migrate-to-monorepo.bat` – Windows batch script for migration

### `linux/` – Linux/Unix-specific scripts
- **Purpose**: Scripts for Linux containers, CI/CD pipelines, and Unix-like systems
- **Languages**: Bash (.sh), Shell
- **Examples**:
  - `generate-docs.sh` – builds documentation (runs in Docker/Linux CI)
  - `backup-postgres.sh` – PostgreSQL backup (Linux cron job)

### `python/` – Cross-platform Python scripts
- **Purpose**: Platform-independent utilities and complex automation
- **Languages**: Python (.py)
- **Examples**:
  - `healthcheck.py` – health checks for services (cross-platform)
  - `sync-from-my-ecosystem.py` – complex data synchronization

### `general/` – Platform-agnostic or legacy scripts
- **Purpose**: Scripts that haven't been categorized yet or work on any platform
- **Languages**: Mixed
- **Note**: This is a transitional directory; scripts should eventually move to appropriate categories

## 🔄 Current Status (After Restructuring)

**Реструктуризация завершена (2026-04-08):**
- ✅ Удалены дублирующие скрипты (см. [DEDUPLICATION_PLAN.md](./DEDUPLICATION_PLAN.md))
- ✅ Все скрипты перемещены в соответствующие категории
- ✅ Создан подробный индекс [INDEX.md](./INDEX.md)

### Актуальная структура:
| Категория | Скриптов | Состояние | Описание |
|-----------|----------|-----------|----------|
| `windows/` | 2 | 🟡 Частично | Windows-специфичные скрипты (PowerShell, Batch) |
| `linux/` | 6 | 🟢 Полное | Linux/Unix скрипты для CI/CD и администрирования |
| `python/` | 5 | 🟢 Полное | Кросс-платформенные Python утилиты |
| Корень | 21 | 🟢 Стабильное | Кросс-платформенные и общие скрипты |

> **Примечание**: Папка `general/` была удалена, так как все скрипты теперь categorized.

## 📖 Evolution Narrative: "От Зеро к Херо"

Эта папка scripts/ представляет собой **археологическую карту** профессионального роста:

### 🥚 Этап 1: Прототипы (Зеро)
```bash
fix_encoding.ps1       # Простейшее решение конкретной проблемы
check_yaml.py          # Базовая проверка с ошибками (удалён)
```

### 🐣 Этап 2: Специализация
```bash
cleanup-old-branches.ps1  # Windows-версия
cleanup-old-branches.sh   # Linux-версия
```
*Разные реализации для разных ОС → доказательство enterprise-экспертизы*

### 🐥 Этап 3: Улучшение
```bash
update-badges.py          → update-badges-enhanced.py
check_yaml.py             → check_yaml_fixed.py
```
*Исправление ошибок, добавление функциональности*

### 🦅 Этап 4: Production-ready (Херо)
```bash
healthcheck.py           # Комплексные проверки с метриками
deploy.sh                # CI/CD пайплайн
setup-vscode-extensions.py # Автоматизация developer experience
```

### 📊 Эволюционные паттерны:
1. **Дублирование → Специализация** – разные версии для разных платформ
2. **Прототип → Production** – добавление обработки ошибок, логирования
3. **Ручное → Автоматическое** – интеграция в CI/CD пайплайны

## 🚀 Usage Guidelines

### For New Scripts
1. **Choose the right language**:
   - **Windows administration**: PowerShell
   - **Linux/containers/CI**: Bash
   - **Cross-platform/complex logic**: Python
2. **Place in appropriate directory**:
   - `windows/` for Windows-specific
   - `linux/` for Linux/Unix-specific  
   - `python/` for cross-platform Python
3. **Document dependencies** in script header

### For Existing Scripts
- Scripts in root directory are **legacy** and will be gradually moved
- Update any references in documentation or CI/CD configurations
- Test after moving to ensure nothing breaks

## 🤔 Why Not Unify on One Language?

While Python could handle all tasks, the mixed approach demonstrates:

1. **Real-world enterprise experience** – companies have mixed environments
2. **Specialized tool expertise** – PowerShell for Windows admin, Bash for Linux ops
3. **Portfolio diversity** – shows breadth of skills beyond just Python
4. **Performance/appropriateness** – some tasks are simpler in native shell

## 📚 Related Documentation

### Архитектурные решения
- [ADR-007: Technology Stack Justification](../docs/architecture/decisions/ADR-007-technology-stack-justification.md) – обоснование mixed scripting
- [ADR-008: Service Discovery](../docs/architecture/decisions/ADR-008-service-discovery.md) – микросервисная архитектура

### Документация реструктуризации
- [INDEX.md](./INDEX.md) – полный индекс скриптов с архитектурной картой
- [DEDUPLICATION_PLAN.md](./DEDUPLICATION_PLAN.md) – план удаления дубликатов
- [restructure-scripts.ps1](./restructure-scripts.ps1) – скрипт реструктуризации

### Использование в проекте
- [CI/CD Configuration](../.github/workflows/) – пайплайны, использующие эти скрипты
- README.md: Architectural Justification section – общее архитектурное обоснование

### Эволюционный контекст
- Git history ветки `refactor-backup` – полная история изменений
- Удалённые скрипты доступны в git history как "археологические слои"

