# 🚀 План: Настройка GitHub Pages для Portfolio System Architect

**Статус:** 🔴 **БЛОКИРУЮЩАЯ ПРОБЛЕМА** — документация не публикуется
**Цель:** Восстановить работу GitHub Pages по адресу `https://control39.github.io/portfolio-system-architect/`
**Приоритет:** Высокий (нужно для демонстрации работодателю)

---

## 📋 Текущая ситуация

- **Workflow:** `.github/workflows/deploy-pages.yml` пытается собрать сайт через MkDocs
- **Проблема:** Файл `mkdocs.yml` **отсутствует** в корне репозитория
- **Результат:** Сборка падает с ошибкой, GitHub Pages не работает

---

## 🔍 Варианты решения

### Вариант 1: Создать `mkdocs.yml` (Рекомендуется ✅)

**Плюсы:**
- Автоматическая генерация навигации
- Поддержка тем (Material для MkDocs)
- Интеграция с Git (история изменений)
- Стандартное решение для документации на GitHub

**Минусы:**
- Нужно создать конфиг и проверить навигацию
- Может потребоваться установка плагинов

**План:**
1. Создать `mkdocs.yml` с базовой конфигурацией
2. Добавить навигацию по разделам (включая новые категории кейсов)
3. Протестировать сборку локально
4. Закоммитить и проверить деплой

### Вариант 2: Деплой статических HTML-файлов

**Плюсы:**
- Полный контроль над HTML
- Не зависит от MkDocs

**Минусы:**
- Нужно вручную генерировать HTML или писать скрипт
- Нет автоматической навигации

**План:**
1. Написать скрипт конвертации Markdown в HTML
2. Изменить workflow на деплой `site/` из скрипта
3. Тестирование

### Вариант 3: Отключить автоматический деплой

**Плюсы:**
- Быстрое решение
- Нет ошибок в Actions

**Минусы:**
- Документация недоступна онлайн
- Нужно публиковать вручную

**План:**
1. Отключить workflow или удалить его
2. Задокументировать, что документация доступна только в README

---

## ✅ Рекомендуемый план (Вариант 1)

### Шаг 1: Создать `mkdocs.yml`

```yaml
site_name: Portfolio System Architect
site_description: Production-ready cognitive architecture ecosystem
site_author: Your Name

repo_name: control39/portfolio-system-architect
repo_url: https://github.com/control39/portfolio-system-architect

theme:
  name: material
  palette:
    primary: blue
    accent: blue

plugins:
  - search
  - git-revision-date-localized

markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
  - toc:
      permalink: true

nav:
  - Home: README.md
  - Quick Start: QUICK_START.md
  - Architecture:
      - Overview: ARCHITECTURE.md
      - Atoms & Molecules: docs/architecture/atoms-and-molecules.md
      - ADRs: docs/architecture/decisions/
  - Cases:
      - Overview: docs/cases/README.md
      - Integration: docs/cases/integration/README.md
      - Business: docs/cases/business/README.md
      - Thinking: docs/cases/thinking/README.md
      - Evolution: docs/cases/evolution/README.md
      - Methodology: docs/cases/methodology/README.md
      - Technical: docs/cases/technical/README.md
  - Services:
      - Overview: apps/README.md
      - AI Config Manager: apps/ai_config_manager/README.md
      - IT Compass: apps/it_compass/README.md
      - Decision Engine: apps/decision_engine/README.md
      # ... остальные сервисы
  - Deployment:
      - Docker: DOCKERFILE_TEMPLATE_MONOREPO.txt
      - Kubernetes: deployment/k8s-README.md
  - Monitoring: monitoring/README.md
  - Contributing: CONTRIBUTING.md
```

### Шаг 2: Установить зависимости (если нужно)

```powershell
pip install mkdocs-material mkdocs-git-revision-date-localized-plugin
```

### Шаг 3: Протестировать сборку локально

```powershell
mkdocs build
# Проверить папку site/
ls site/
```

### Шаг 4: Закоммитить и проверить деплой

```powershell
git add mkdocs.yml
git commit -m "docs: добавить mkdocs.yml для GitHub Pages"
git push origin main
```

### Шаг 5: Проверить GitHub Actions

- Открыть: `https://github.com/control39/portfolio-system-architect/actions/workflows/deploy-pages.yml`
- Проверить, что последний запуск успешен
- Проверить, что страница доступна: `https://control39.github.io/portfolio-system-architect/`

---

## 📂 Новая структура кейсов (для навигации)

После консолидации кейсы организованы так:

```
docs/cases/
├── README.md                     # Главный индекс
├── integration/                  # Интеграционные кейсы
│   ├── README.md
│   ├── case-1-it-compass-portfolio-organizer/
│   ├── case-2-infra-orchestrator-decision-engine/
│   └── case-3-system-proof-thought-architecture/
├── business/                     # Бизнес-кейсы (ROI)
│   ├── README.md
│   ├── business-impact/
│   └── autoarchitect.md
├── thinking/                     # Системное мышление
│   ├── README.md
│   └── thinking-cases/
├── evolution/                    # Эволюционные кейсы
│   ├── README.md
│   └── evolution-cases/
├── methodology/                  # IT-Compass
│   ├── README.md
│   └── it-compass/
└── technical/                    # Технические разборы
    ├── README.md
    ├── ai-config-manager/
    └── infra-sync-hardening-2026.md
```

**Важно:** Обновить `mkdocs.yml` с учётом этой структуры.

---

## 🎯 Критерии успеха

- [ ] `mkdocs.yml` создан и валиден
- [ ] Сборка локально успешна (`mkdocs build` без ошибок)
- [ ] GitHub Actions workflow проходит успешно
- [ ] Страница доступна по `https://control39.github.io/portfolio-system-architect/`
- [ ] Навигация по кейсам работает (все категории доступны)
- [ ] Ссылки внутри документации не битые

---

## 📞 Если что-то пойдёт не так

1. **Ошибка сборки:** Проверить логи в GitHub Actions, убедиться, что все плагины установлены
2. **Битые ссылки:** Проверить пути в `mkdocs.yml` относительно структуры файлов
3. **Не виден сайт:** Проверить настройки GitHub Pages в репозитории (Settings → Pages → Source)

---

## 📝 Примечания

- **Текущая папка с планами агентов:** `.codeassistant/plans/` (сюда перенесён `AGENT_QUICK_START.md`)
- **Старые планы проекта:** `.reports/plans/` и `.koda/plans/` (не трогать)
- **Кейсы консолидированы:** `docs/cases/` с новой структурой

---

**Создан:** 24 мая 2026 г.
**Приоритет:** Высокий (блокирует демонстрацию проекта)
**Ответственный:** Человек + AI-ассистент
