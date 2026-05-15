# Repository Audit Tool

Инструмент аудита репозитория для оценки зрелости проекта по трём уровням: **base**, **professional**, **enterprise**.

## 🎯 Назначение

Audit Tool проверяет репозиторий на соответствие стандартам качества в 9 категориях:

- ✅ **Доступность файлов** — проверка существования критичных файлов
- ✅ **CI/CD** — наличие GitHub Actions, GitLab CI и т.д.
- ✅ **Качество кода** — линтеры, форматирование, статический анализ
- ✅ **Зависимости** — управление зависимостями, уязвимости
- ✅ **Документация** — README, ARCHITECTURE, CONTRIBUTING
- ✅ **Лицензирование** — LICENSE, авторские права
- ✅ **Мониторинг** — Prometheus, Grafana, логирование
- ✅ **Безопасность** — сканирование секрета, уязвимостей
- ✅ **Тестирование** — покрытие кода, типы тестов

## 🏗️ Архитектура

```
┌─────────────────────┐
│   CLI / Python API  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   RepositoryAudit   │
│   (core class)      │
└──────────┬──────────┘
           │
    ┌──────┴──────────────┬──────────────┬─────────────┐
    │                     │              │             │
    ▼                     ▼              ▼             ▼
┌─────────┐       ┌──────────┐   ┌──────────┐  ┌──────────┐
│  base   │       │professional│ │ enterprise│ │  checks  │
│  level  │       │   level   │ │   level   │ │  modules │
└─────────┘       └──────────┘   └──────────┘  └──────────┘
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd tools/repo_audit
pip install -r requirements.txt
```

### 2. Запуск аудита

```bash
# Из корня проекта
python -m tools.repo_audit.cli --level base

# Или через скрипт
./tools/repo_audit/audit.sh --level professional

# Или напрямую
python tools/repo_audit/audit.py --level enterprise
```

### 3. Результат

```
============================================================
🔍 Аудит репозитория (professional уровень)
============================================================

✅ Проверки: 45/50
❌ Пропущено: 5

📊 Итоговая оценка: 90%

✅ Passed:
  • README.md существует
  • LICENSE существует
  • GitHub Actions настроен
  • Coverage > 80%
  ...

❌ Failed:
  • SECURITY.md отсутствует
  • Dependabot не настроен
  ...

📈 Рекомендации:
  1. Добавьте SECURITY.md
  2. Настройте Dependabot
  ...
============================================================
```

## 📋 Категории проверок

### 1. **Automation** (`checks/automation.py`)

- Наличие скриптов автоматизации
- Makefile или task runner
- Pre-commit hooks

### 2. **CI/CD** (`checks/cicd.py`)

- GitHub Actions / GitLab CI / Jenkins
- Pipeline для тестов и линтинга
- Автоматическое деплоирование

### 3. **Code Quality** (`checks/code_quality.py`)

- Линтеры (Ruff, Black, ESLint)
- Статический анализ (MyPy, Pylint)
- Форматирование кода

### 4. **Dependencies** (`checks/dependencies.py`)

- Файлы зависимостей (requirements.txt, package.json)
- Обновление зависимостей
- Проверка уязвимостей (Dependabot, Snyk)

### 5. **Documentation** (`checks/documentation.py`)

- README.md
- ARCHITECTURE.md
- CONTRIBUTING.md
- ADR (Architectural Decision Records)

### 6. **Licensing** (`checks/licensing.py`)

- LICENSE файл
- Авторские права
- Лицензия в package.json/pyproject.toml

### 7. **Monitoring** (`checks/monitoring.py`)

- Prometheus / Grafana
- Логирование
- Health checks

### 8. **Security** (`checks/security.py`)

- Secret scanning (.gitignore, .secrets.baseline)
- Vulnerability scanning (Trivy, Bandit)
- SECURITY.md

### 9. **Testing** (`checks/testing.py`)

- Тесты (pytest, unittest)
- Покрытие кода (Coverage)
- E2E тесты

## ⚙️ Конфигурация

### Уровни аудита

| Уровень | Проверки | Цель |
|---------|----------|------|
| **base** | ~20 | Минимальные требования (README, LICENSE) |
| **professional** | ~50 | Стандарты индустрии (тесты, CI/CD, безопасность) |
| **enterprise** | ~100 | Корпоративные стандарты (мониторинг, ADR, compliance) |

### Параметры CLI

```bash
python -m tools.repo_audit.cli [OPTIONS]

Options:
  --level [base|professional|enterprise]  Уровень аудита
  --output [json|text|html]              Формат вывода
  --output-file FILE                      Файл для результата
  --verbose                               Подробный вывод
  --help                                  Показать помощь
```

### Примеры

```bash
# Базовый аудит
python -m tools.repo_audit.cli --level base

# Профессиональный аудит с JSON-выводом
python -m tools.repo_audit.cli --level professional --output json --output-file audit-report.json

# Enterprise аудит с подробным выводом
python -m tools.repo_audit.cli --level enterprise --verbose
```

## 🧪 Тестирование

### Запуск тестов

```bash
cd tools/repo_audit
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Пример теста

```python
def test_file_exists(checker):
    result = checker.check_file_exists("README.md", "README")
    assert result["status"] == "PASS"
```

## 🐳 Docker-развёртывание

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY tools/repo_audit/requirements.txt .
RUN pip install -r requirements.txt

COPY tools/repo_audit/ .

ENTRYPOINT ["python", "cli.py"]
```

### Использование

```bash
docker build -t repo-audit -f tools/repo_audit/Dockerfile .
docker run -v $(pwd):/app repo-audit --level professional
```

## 📊 Формат вывода (JSON)

```json
{
  "level": "professional",
  "score": 90,
  "total_checks": 50,
  "passed": 45,
  "failed": 5,
  "results": [
    {
      "check": "README.md существует",
      "status": "PASS",
      "path": "README.md"
    },
    {
      "check": "SECURITY.md отсутствует",
      "status": "FAIL",
      "path": "SECURITY.md"
    }
  ],
  "recommendations": [
    "Добавьте SECURITY.md",
    "Настройте Dependabot"
  ]
}
```

## 🛠️ Troubleshooting

### Ошибка: "Модуль не найден"

**Решение:**
```bash
cd tools/repo_audit
pip install -r requirements.txt
```

### Ошибка: "Недостаточно прав"

**Решение:** Убедитесь, что у вас есть права на чтение всех файлов репозитория.

### Ошибка: "Неверный уровень"

**Решение:** Используйте один из уровней: `base`, `professional`, `enterprise`.

## 📈 Метрики

### Тесты

- **Количество:** ≥20 тестов
- **Покрытие:** ≥80%
- **Прохождение:** 100%

### Производительность

- **Время аудита:** ~5 сек (professional)
- **Память:** ~20MB

## 🤝 Вклад

1. Добавьте новую проверку в `checks/`
2. Напишите тесты для проверки
3. Обновите документацию
4. Отправьте PR

## 📝 История изменений

### v0.1.0 (2026-05-16)
- ✨ Первоначальная реализация
- 🔧 9 модулей проверок
- 📊 Поддержка 3 уровней
- 🧪 Базовые тесты

---

*Документация создана: 16 мая 2026 г.*
