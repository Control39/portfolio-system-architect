# Индекс скриптов: Архитектурная карта

## 🧭 Навигация по профессиональному росту

Этот индекс представляет собой **археологическую карту** эволюции скриптов от простых прототипов до production-ready решений. Каждая категория демонстрирует определённый этап профессионального роста.

### Ключ к чтению:
- 🟢 **Стабильная версия** – используется в CI/CD, имеет обработку ошибок, логирование
- 🟡 **Улучшенный** – функционально полный, но может быть оптимизирован
- 🔴 **Прототип** – доказательство концепции, историческая ценность
- 🔵 **Кросс-платформенный** – работает на Windows и Linux
- ⚫ **Специализированный** – оптимизирован под конкретную платформу

## 📊 Таблица скриптов

### Корневая директория (Кросс-платформенные/Общие)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `check-badges-health.py` | Python | Комплексная проверка здоровья бейджей | 🔵 Кросс-платформа | 🟢 Стабильная версия | Демонстрирует мониторинг внешних зависимостей |
| `check-dependency-updates.py` | Python | Проверка обновлений зависимостей | 🔵 Кросс-платформа | 🟡 Улучшенный | Proactive dependency management |
| `check_badge_urls.py` | Python | Валидация URL бейджей | 🔵 Кросс-платформа | 🟡 Улучшенный | Специализированная валидация |
| `check_yaml_fixed.py` | Python | Проверка синтаксиса YAML | 🔵 Кросс-платформа | 🟢 Стабильная версия | Исправленная версия с обработкой ошибок |
| `cleanup-old-branches.ps1` | PowerShell | Очистка старых Git веток | ⚫ Windows | 🟢 Стабильная версия | Windows-специфичная Git автоматизация |
| `cleanup-old-branches.sh` | Bash | Очистка старых Git веток | ⚫ Linux | 🟢 Стабильная версия | Linux-специфичная Git автоматизация |
| `deploy.sh` | Bash | Деплой приложения | ⚫ Linux | 🟢 Стабильная версия | CI/CD пайплайн для Linux |
| `enhance-badge-links.py` | Python | Улучшение ссылок на бейджи | 🔵 Кросс-платформа | 🟡 Улучшенный | SEO-оптимизация документации |
| `fix_import_issues.py` | Python | Исправление проблем импорта | 🔵 Кросс-платформа | 🟡 Улучшенный | Рефакторинг и миграция кода |
| `git-automation.sh` | Bash | Автоматизация Git операций | ⚫ Linux | 🟢 Стабильная версия | Enterprise Git workflows |
| `health-check.sh` | Bash | Быстрая проверка здоровья | ⚫ Linux | 🟢 Стабильная версия | Lightweight healthcheck для CI/CD |
| `rag-automation.sh` | Bash | Автоматизация RAG пайплайна | ⚫ Linux | 🟢 Стабильная версия | AI/ML pipeline automation |
| `security-check.sh` | Bash | Базовая проверка безопасности | ⚫ Linux | 🟡 Улучшенный | Security scanning в CI/CD |
| `setup-environment.sh` | Bash | Настройка окружения | ⚫ Linux | 🟢 Стабильная версия | Environment as Code |
| `setup-monitoring.sh` | Bash | Настройка мониторинга | ⚫ Linux | 🟢 Стабильная версия | Observability setup |
| `setup-vscode-extensions.py` | Python | Установка расширений VSCode | 🔵 Кросс-платформа | 🟢 Стабильная версия | Developer experience automation |
| `start-all.sh` | Bash | Запуск всех сервисов | ⚫ Linux | 🟡 Улучшенный | Orchestration скрипт |
| `stop-all.sh` | Bash | Остановка всех сервисов | ⚫ Linux | 🟡 Улучшенный | Graceful shutdown |
| `sync_projects_by_hash.py` | Python | Синхронизация проектов по хешу | 🔵 Кросс-платформа | 🟡 Улучшенный | Data synchronization pattern |
| `update-badges-enhanced.py` | Python | Обновление бейджей в README | 🔵 Кросс-платформа | 🟢 Стабильная версия | Автоматическое поддержание актуальности |
| `validate_dependabot.py` | Python | Валидация конфигурации Dependabot | 🔵 Кросс-платформа | 🟡 Улучшенный | Security automation |

### `windows/` (Windows-специфичные)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `fix_encoding.ps1` | PowerShell | Исправление кодировки файлов | ⚫ Windows | 🔴 Прототип | Демонстрация работы с Windows-специфичными проблемами |
| `migrate-to-monorepo.bat` | Batch | Миграция в monorepo | ⚫ Windows | 🟡 Улучшенный | Legacy Windows automation |

### `linux/` (Linux/Unix-специфичные)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `backup-postgres.sh` | Bash | Резервное копирование PostgreSQL | ⚫ Linux | 🟢 Production-ready | Database backup strategy |
| `check-lfs.sh` | Bash | Проверка Git LFS | ⚫ Linux | 🟡 Улучшенный | Large file storage management |
| `generate-docs.sh` | Bash | Генерация документации | ⚫ Linux | 🟢 Production-ready | Documentation as Code |
| `generate-index.sh` | Bash | Генерация индекса файлов | ⚫ Linux | 🟡 Улучшенный | File system navigation |
| `generate-site.sh` | Bash | Генерация сайта документации | ⚫ Linux | 🟢 Production-ready | Static site generation |
| `restore-postgres.sh` | Bash | Восстановление PostgreSQL | ⚫ Linux | 🟢 Production-ready | Disaster recovery procedure |

### `python/` (Кросс-платформенные Python)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `healthcheck.py` | Python | Комплексная проверка здоровья | 🔵 Кросс-платформа | 🟢 Production-ready | Production health checks с метриками |
| `migrate-sqlite-to-postgres.py` | Python | Миграция данных между БД | 🔵 Кросс-платформа | 🟢 Production-ready | Database migration pattern |
| `sync-from-my-ecosystem.py` | Python | Синхронизация с внешней экосистемой | 🔵 Кросс-платформа | 🟡 Улучшенный | External system integration |
| `test_yandex_gpt_integration.py` | Python | Тестирование интеграции с Yandex GPT | 🔵 Кросс-платформа | 🟢 Production-ready | AI service integration testing |
| `translate-docs.py` | Python | Перевод документации | 🔵 Кросс-платформа | 🟡 Улучшенный | Internationalization automation |

### `dev/` (Инструменты разработки)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `reorganize-structure.ps1` | PowerShell | Реорганизация структуры проекта | ⚫ Windows | 🟡 Улучшенный | Project refactoring automation |
| `setup-dev.ps1` | PowerShell | Настройка dev окружения | ⚫ Windows | 🟢 Production-ready | Developer onboarding |
| `setup-profile.ps1` | PowerShell | Настройка профиля PowerShell | ⚫ Windows | 🟢 Production-ready | Shell customization |

### `security/` (Безопасность)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `ci_security.sh` | Bash | Security checks в CI | ⚫ Linux | 🟢 Production-ready | Shift-left security |
| `scan_secrets.py` | Python | Сканирование секретов | 🔵 Кросс-платформа | 🟢 Production-ready | Secrets management |

### `deployment/` (Деплой)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `backup-postgres.sh` | Bash | Резервное копирование PostgreSQL | ⚫ Linux | 🟢 Стабильная версия | Database backup strategy |
| `check-lfs.sh` | Bash | Проверка Git LFS | ⚫ Linux | 🟡 Улучшенный | Large file storage management |
| `generate-docs.sh` | Bash | Генерация документации | ⚫ Linux | 🟢 Стабильная версия | Documentation as Code |
| `generate-index.sh` | Bash | Генерация индекса файлов | ⚫ Linux | 🟡 Улучшенный | File system navigation |
| `generate-site.sh` | Bash | Генерация сайта документации | ⚫ Linux | 🟢 Стабильная версия | Static site generation |
| `restore-postgres.sh` | Bash | Восстановление PostgreSQL | ⚫ Linux | 🟢 Стабильная версия | Disaster recovery procedure |

### `python/` (Кросс-платформенные Python)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `healthcheck.py` | Python | Комплексная проверка здоровья | 🔵 Кросс-платформа | 🟢 Стабильная версия | Production health checks с метриками |
| `migrate-sqlite-to-postgres.py` | Python | Миграция данных между БД | 🔵 Кросс-платформа | 🟢 Стабильная версия | Database migration pattern |
| `sync-from-my-ecosystem.py` | Python | Синхронизация с внешней экосистемой | 🔵 Кросс-платформа | 🟡 Улучшенный | External system integration |
| `test_yandex_gpt_integration.py` | Python | Тестирование интеграции с Yandex GPT | 🔵 Кросс-платформа | 🟢 Стабильная версия | AI service integration testing |
| `translate-docs.py` | Python | Перевод документации | 🔵 Кросс-платформа | 🟡 Улучшенный | Internationalization automation |

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `reorganize-structure.ps1` | PowerShell | Реорганизация структуры проекта | ⚫ Windows | 🟡 Улучшенный | Project refactoring automation |
| `setup-dev.ps1` | PowerShell | Настройка dev окружения | ⚫ Windows | 🟢 Стабильная версия | Developer onboarding |
| `setup-profile.ps1` | PowerShell | Настройка профиля PowerShell | ⚫ Windows | 🟢 Стабильная версия | Shell customization |

### `security/` (Безопасность)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `ci_security.sh` | Bash | Security checks в CI | ⚫ Linux | 🟢 Стабильная версия | Shift-left security |
| `scan_secrets.py` | Python | Сканирование секретов | 🔵 Кросс-платформа | 🟢 Стабильная версия | Secrets management |

### `deployment/` (Деплой)

| Скрипт | Язык | Задача | Платформа | Статус | Архитектурная ценность |
|--------|------|--------|-----------|--------|------------------------|
| `deploy-azure.ps1` | PowerShell | Деплой в Azure | ⚫ Windows | 🟢 Стабильная версия | Cloud deployment automation |

## 📈 Эволюционные паттерны

### Паттерн 1: От прототипа к production
```
fix_encoding.ps1 (🔴) → setup-vscode-extensions.py (🟢)
```
*Прототип для решения конкретной проблемы → Полноценный инструмент с обработкой ошибок*

### Паттерн 2: Кросс-платформенная специализация
```
cleanup-old-branches.ps1 (Windows) + cleanup-old-branches.sh (Linux)
```
*Разные реализации для разных ОС → Доказательство enterprise-экспертизы*

### Паттерн 3: Функциональное развитие
```
update-badges.py (удалён) → update-badges-enhanced.py (🟢)
```
*Базовая функциональность → Улучшенная версия с дополнительными возможностями*

## 🎯 Рекомендации по использованию

### Для найма архитектора:
1. **Посмотрите `python/`** – кросс-платформенные сложные задачи
2. **Обратите внимание на пары скриптов** – доказательство понимания различий ОС
3. **Проанализируйте эволюцию** – как скрипты развивались от простых к сложным

### Для собственного использования:
1. **Стабильные скрипты** – можно сразу использовать в CI/CD
2. **Прототипы** – изучайте как примеры решения специфичных проблем
3. **Специализированные скрипты** – адаптируйте под свои нужды

## 🔗 Связанные документы

- [DEDUPLICATION_PLAN.md](./DEDUPLICATION_PLAN.md) – план удаления дубликатов
- [README.md](./README.md) – общая структура и rationale
- [restructure-scripts.ps1](./restructure-scripts.ps1) – скрипт реструктуризации

---
*Индекс сгенерирован: 2026-04-08*
*Архитектурный принцип: "Карта показывает не только что есть, но и как рос"*
