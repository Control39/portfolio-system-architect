# AI Config Manager

## Contributing
См. [CONTRIBUTING.md](../../CONTRIBUTING.md)


## Deployment
```bash
docker build -t ai-config-manager .
docker run -p 8000:8000 ai-config-manager
```


## Dependencies
```bash
pip install -r requirements.txt
```


## Features
- Загрузка конфигов из YAML
- Hot reload
- Fallback на локальные конфиги


## Purpose
Централизованное управление конфигурациями всех сервисов.


> **Статус:** 🟢 Production Ready (PyPI-ready)
> **Версия:** 1.0.0
> **Владелец:** Portfolio System Architect Team
> **Последнее обновление:** 16 мая 2026 г.

[![PyPI Ready](https://img.shields.io/badge/PyPI-ready-brightgreen)]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![Pydantic](https://img.shields.io/badge/pydantic-v2-orange)]()

---

## 🎯 Назначение

Система централизованного управления конфигурацией AI-агентов и сервисов. Обеспечивает динамическую перезагрузку конфигов (hot reload), валидацию, управление ресурсами и потокобезопасность.

### Ключевые возможности
- [x] Централизованное управление конфигурацией
- [x] Hot reload — динамическая перезагрузка конфигов
- [x] Валидация конфигураций через Pydantic
- [x] Управление ресурсами (модели, API ключи)
- [x] Потокобезопасные операции (thread safety)

---

## 💼 Архитектурная ценность

### Проблема, которую решает AI Config Manager

В эпоху взрывного роста ИИ-агентов (AutoGPT, LangChain, LlamaIndex) разработчики сталкиваются с хаосом в настройках:
- **Фрагментация:** Ключи API, промпты и параметры моделей разбросаны по файлам `.env`, YAML-конфигам и коду.
- **Отсутствие версионирования:** Невозможно отследить, какая версия промпта использовалась в production.
- **Безопасность:** Секреты часто попадают в логи или систему контроля версий.
- **Масштабирование:** При добавлении нового агента требуется ручная настройка десятков параметров.

### Решение

AI Config Manager предоставляет **единый источник истины** для всех ИИ-конфигураций:
- **Централизация:** Все настройки агентов, моделей и инструментов в одном месте.
- **Hot Reload:** Изменения применяются без перезапуска агентов.
- **Валидация:** Pydantic гарантирует корректность конфигов до запуска.
- **Безопасность:** Встроенное маскирование секретов и поддержка внешних vault (AWS KMS, Azure Key Vault).

### Преимущества архитектуры

| Без AI Config Manager | С AI Config Manager |
|-----------------------|---------------------|
| Конфиги разбросаны по проекту | Единый файл `ai-config.yaml` |
| Ручное обновление после изменений | Автоматический hot reload |
| Секреты в логах и коде | Маскирование + внешние vault |
| Сложность добавления новых агентов | Подключение через YAML |

### Готовая формулировка для портфолио

> **«Универсальный менеджер конфигураций ИИ (AI Config Manager)»**<br>
> Разработана система централизованного управления конфигурациями для ИИ-агентов и LLM-приложений. Решает проблему фрагментации настроек (ключи API, промпты, параметры моделей) через единый YAML-файл с поддержкой hot reload, валидации через Pydantic и интеграции с vault (AWS KMS, Azure Key Vault). Позволяет масштабировать количество агентов без роста операционной нагрузки.

---

## 🏗️ Архитектура

| Категория | Значение |
|-----------|----------|
| **Технологии** | Python 3.10+, Pydantic, Docker (опционально) |
| **Зависимости** | Auth Service (опционально), AI Agents |
| **Порт (Internal)** | N/A (Python module) |
| **Порт (External)** | N/A |
| **Traefik Route** | N/A |
| **Health Check** | N/A |

### Схема развёртывания

```
┌─────────────────────────┐
│   AI Agents / Services  │
│   (импорт модуля)       │
└────────┬────────────────┘
         │ from ai_config_manager import ConfigManager
         ▼
┌─────────────────────────┐
│  AI Config Manager      │
│  (Python Module)        │
│  - ConfigManager        │
│  - ResourcePool         │
│  - Hot Reload           │
└─────────────────────────┘
```

> 💡 **Примечание:** Это Python-модуль, не FastAPI-сервис. Используется через импорт в коде.

---

## 🚀 Quick Start

### Использование в коде

```python
# 1. Импортировать модуль
from apps.ai_config_manager.src.config_manager import ConfigManager

# 2. Создать менеджер конфигурации
config = ConfigManager(config_path="config/ai-config.yaml")

# 3. Получить конфигурацию агента
agent_config = config.get_agent_config("cognitive-agent")

# 4. Обновить конфигурацию (hot reload)
config.reload()

# 5. Валидация конфигурации
is_valid = config.validate()
```

### Конфигурационный файл (YAML)

```yaml
# config/ai-config.yaml
agents:
  cognitive-agent:
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 2048
    resources:
      - name: "code-analyzer"
        type: "tool"
        enabled: true

  job-agent:
    model: "gpt-3.5-turbo"
    temperature: 0.5
    max_tokens: 1024

resources:
  - name: "code-analyzer"
    type: "tool"
    config:
      language: "python"
      linting: true
```

---

## 🛡️ Безопасность

### Реализованные меры

- [x] **Маскирование секретов** — использование `mask_sensitive()` из `src/security/secret_masking.py`
- [x] **Валидация входных данных** — Pydantic models для всех конфигов
- [x] **Защита от инъекций** — санитизация путей к конфигам
- [x] **Шифрование секретов** — опциональная поддержка SOPS/AWS KMS

### Security Checklist

При добавлении нового функционала проверить:

- [x] Нет hardcoded secrets в коде
- [x] Все внешние вызовы валидируют SSL
- [x] Input sanitization для пользовательских данных
- [x] Логирование security-событий (без секретов!)

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Из корневого каталога
pytest apps/ai-config-manager/tests/ --cov=apps/ai-config-manager --cov-report=term-missing

# С HTML отчётом
pytest apps/ai-config-manager/tests/ --cov=apps/ai-config-manager --cov-report=html
```

### Покрытие кода

| Метрика | Значение | Цель |
|---------|----------|------|
| **Unit Tests** | 15/15 | ≥80% ✅ |
| **Integration Tests** | 0/0 | N/A |
| **Total Coverage** | ~95% | ≥80% ✅ |

### Типы тестов

| Тип тестов | Файл | Количество | Описание |
|-----------|------|------------|----------|
| **Базовые** | `test_basic.py` | 15 | Конфигурация, валидация, hot reload, ресурсы |

**Итого:** 15 тестов, 100% прохождение ✅

---

## 📦 Зависимости

### Production зависимости

```txt
pydantic>=2.0.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
```

### Development зависимости

```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
```

### Внешние сервисы

- [ ] **Auth Service** — аутентификация для доступа к секретам (опционально)
- [ ] **AWS KMS / Azure Key Vault** — управление секретами (опционально)

---

## ⚙️ Конфигурация

### Переменные окружения

Создайте `.env` в корневом каталоге проекта:

```env
# Config Path
CONFIG_PATH=config/ai-config.yaml

# Secret Management (опционально)
AWS_KMS_KEY_ID=your-kms-key-id
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/

# Logging
LOG_LEVEL=INFO
```

### Конфигурационные файлы

| Файл | Описание |
|------|----------|
| `.env` | Переменные окружения (не коммитить!) |
| `config/ai-config.yaml` | Конфигурация AI-агентов |
| `pyproject.toml` | Зависимости и настройки сборки |

---

## 📊 Мониторинг

### Метрики

- **Structured logging:** JSON format в stdout
- **Config reload events:** Логирование изменений конфигурации
- **Resource usage:** Количество активных агентов/ресурсов

### Дашборды

- **Grafana:** http://localhost:3000 (если настроено логирование)
- **Traefik Dashboard:** N/A

---

## 🔄 CI/CD

### Workflow

```yaml
# .github/workflows/ai-config-manager-ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest apps/ai-config-manager/tests/
      - name: Run linters
        run: ruff check apps/ai-config-manager/
```

### Развёртывание

- **Environment:** Staging → Production
- **Strategy:** Rolling update (при изменении конфигов)
- **Rollback:** Автоматический при валидации конфига

---

## 📚 Дополнительные ресурсы

### Документация

- [ARCHITECTURE.md](../../ARCHITECTURE.md) — общий обзор архитектуры
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — правила контрибуции
- [SECURITY.md](../../SECURITY.md) — политика безопасности

### Связанные сервисы

- **[Cognitive Agent]** — использует конфигурацию для работы
- **[Job Automation Agent]** — конфигурация AI-моделей
- **[Decision Engine]** — конфигурация RAG и reasoning
- **[All AI Services]** — централизованное управление

### Известные проблемы

| Проблема | Статус | Временное решение |
|----------|--------|-------------------|
| Нет HTTP API (только Python module) | Feature | Использовать как библиотеку |

---

## 📝 Changelog

### [1.0.0] — 2026-05-15

- **Added:** 15 тестов с 100% прохождением
- **Added:** ConfigManager с hot reload
- **Added:** ResourcePool для управления ресурсами
- **Added:** Валидация конфигураций через Pydantic
- **Changed:** Стандартизация документации по шаблону

---

## 👥 Контрибьюторы

- **Ekaterina Kudelya** — Architect & Lead Developer
- **Koda AI Agent** — Automated testing & documentation

---

*© 2026 Ekaterina Kudelya. Portfolio System Architect*
