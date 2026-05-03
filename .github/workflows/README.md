# 🚦 CI/CD Documentation

> **Дата создания:** 3 мая 2026 г.  
> **Статус:** ✅ Production-ready  
> **Последнее обновление:** 3 мая 2026 г.

---

## 📋 Обзор

Проект использует GitHub Actions для автоматизации:
- **Тестирование** — unit/integration тесты с покрытием
- **Качество кода** — линтинг (ruff, black, bandit)
- **Безопасность** — сканирование уязвимостей (trivy, pip-audit, gitleaks)
- **Деплой** — автоматический деплой на Azure

---

## 🔧 Workflows

### 1. CI (Continuous Integration)

**Файл:** `.github/workflows/ci.yml`

**Триггеры:**
- Push в `main` / `develop`
- Pull Request в `main` / `develop`

**Что делает:**
- ✅ Устанавливает Python 3.12
- ✅ Кэширует зависимости pip
- ✅ Запускает юнит-тесты с покрытием
- ✅ Генерирует отчеты (junit.xml, coverage.xml)
- ✅ Загружает результаты в Codecov

**Игнорируемые тесты:**
```bash
--ignore=tests/unit/test_assistant_orchestrator_main.py  # CLI mock mismatch
--ignore=tests/unit/test_embedding_agent_updated.py      # ChromaDB/HF deps
```

**См. также:** [KNOWN_ISSUES.md](../docs/KNOWN_ISSUES.md)

---

### 2. Code Quality

**Файл:** `.github/workflows/code-quality.yml`

**Триггеры:**
- Push / PR в `main` / `develop`
- Ручной запуск (`workflow_dispatch`)

**Что делает:**
- ✅ **Black** — проверка форматирования
- ✅ **Ruff** — линтинг Python
- ✅ **Bandit** — security scan (поиск уязвимостей в коде)
- ✅ **Powershell Lint** — отключено временно

**Отчеты:**
- `ruff-lint-report/` — JSON отчет ruff
- `bandit-security-report/` — JSON отчет bandit

---

### 3. Security Scan

**Файл:** `.github/workflows/security-scan.yml`

**Триггеры:**
- Push / PR в `main` / `develop`
- Ежедневно в 01:00 UTC
- Ручной запуск

**Что делает:**
- ✅ **Trivy FS** — сканирование файлов на уязвимости
- ✅ **Bandit** — Python security scan
- ✅ **pip-audit** — проверка зависимостей на CVE
- ✅ **Trivy Docker** — сканирование образов
- ✅ **Gitleaks** — поиск секрета в коде

**Результаты:**
- GitHub Security Tab (SARIF)
- Артефакты (JSON отчеты)

---

### 4. Deploy (Azure)

**Файл:** `.github/workflows/deploy.yml`

**Триггеры:**
- Merge в `main`
- Ручной запуск

**Что делает:**
- ✅ `azd up` / `azd deploy`
- ✅ Terraform / Bicep deployment
- ✅ Проверка статуса деплоя

**См. также:** [deploy-k8s.yml](deploy-k8s.yml) — Kubernetes деплой

---

## 📊 Метрики качества

| Показатель | Порог | Текущее значение |
|------------|-------|------------------|
| **Покрытие тестами** | ≥90% | 93% |
| **Lint errors** | 0 | 0 |
| **Security issues** | 0 (prod) | 0 |
| **E2E тесты** | - | Отключены (требуют Docker) |

---

## 🛠️ Локальная разработка

### Предкоммитные проверки

```bash
# Все проверки (как в CI)
make ci

# Или по отдельности:
make lint      # ruff + black + bandit
make test      # pytest с покрытием
make pre-commit # pre-commit hooks
```

### Pre-commit hooks

```bash
# Установка
pre-commit install

# Запуск вручную
pre-commit run --all-files
```

**Что проверяет pre-commit:**
- Trailing whitespace
- Файлы без trailing newline
- YAML валидация
- JSON валидация
- Большие файлы (>500KB)
- Приватные ключи
- Merge конфликты
- Black форматирование
- isort сортировка импортов
- Ruff линтинг
- Bandit security scan

---

## 🚨 Уведомления

### При неудаче

- **Email** — не настроено
- **GitHub Status** — ✅ включено (check runs)
- **Discord/Slack** — не настроено

### При успехе

- **Codecov** — отчет о покрытии
- **GitHub Deployments** — статус деплоя

---

## 📝 Логи и отладка

### Просмотр логов

1. GitHub Actions → Actions tab
2. Выбрать workflow run
3. Посмотреть логи job'ов

### Перезапуск failed jobs

```
GitHub UI → Workflow run → Retry failed jobs
```

### Локальное воспроизведение

```bash
# Установить act (локальный runner)
choco install act

# Запустить workflow локально
act push -j test
```

---

## 🔐 Секреты

**Требуемые секреты:**

| Секрет | Назначение | Обязательный |
|--------|------------|--------------|
| `CODECOV_TOKEN` | Загрузка покрытия в Codecov | Нет |
| `AZURE_CREDENTIALS` | Деплой на Azure | Да (prod) |
| `GITHUB_TOKEN` | Автоматические PR | Да (встроен) |

**Где настроить:**
`Settings → Secrets and variables → Actions`

---

## 📚 Дополнительные ресурсы

- [GitHub Actions Docs](https://docs.github.com/actions)
- [Codecov Docs](https://docs.codecov.com)
- [Trivy Docs](https://trivy.dev)
- [Bandit Docs](https://bandit.readthedocs.io)

---

*Документация обновлена 3 мая 2026 г.*