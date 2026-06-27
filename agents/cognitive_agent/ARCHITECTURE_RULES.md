# 🤖 Архитектурные правила для Cognitive Agent

## 📋 Краткая сводка (для быстрого старта ИИ)

> **ВСЕГДА ЧИТАЙТЕ ДО НАЧАЛА РАБОТЫ:**
> - [`docs/architecture/ai-developer-rules.md`](../../docs/architecture/ai-developer-rules.md) — Общие правила 3-уровневой архитектуры
> - [`ARCHITECTURE.md`](../../ARCHITECTURE.md) — Общая архитектура проекта
> - [`.ai-context.md`](../../.ai-context.md) — Контекст автора

---

## 🎯 Место Cognitive Agent в архитектуре

```
УРОВЕНЬ 3: АГЕНТЫ (agents/cognitive_agent/)
    ↓ использует
УРОВЕНЬ 2: СЕРВИСЫ (apps/)
    ↓ используют
УРОВЕНЬ 1: АТОМЫ (src/)
```

**Cognitive Agent - это ГЛАВНЫЙ АГЕНТ**, оркеструющий всю систему.

---

## 📂 Структура Cognitive Agent

```
agents/cognitive_agent/
├── src/                              # Модули агента
│   ├── base_agent.py                # Базовый класс агента
│   ├── code_analyzer.py             # Анализ кода
│   ├── documentation_analyzer.py    # Анализ документации
│   └── test_analyzer.py             # Анализ тестов
│
├── skills/                          # 25+ навыков
│   ├── task-planner/                # Планировщик задач
│   ├── project-scanner/             # Сканер проектов
│   ├── code-security-auditor/       # Аудит безопасности кода
│   └── ... (22+ других навыков)
│
├── config/                          # Конфигурация
│   ├── guardrails.yaml              # Правила безопасности (guardrails)
│   ├── ai-config.yaml               # Конфигурация AI
│   └── safe_mode.yaml               # Безопасный режим (только чтение)
│
├── tests/                           # Тесты агента
│   ├── test_rate_limiter.py
│   ├── test_secret_manager.py
│   ├── test_secure_path.py
│   └── test_enterprise_guardrails.py
│
├── docs/                            # Документация
│   ├── FUTURE_PRIORITY_TASKS.md
│   ├── SECURITY_CHANGES_REPORT.md
│   └── ... (другие отчёты)
│
├── AGENT_DOCUMENTATION.md           # Полная документация агента
├── README.md                        # Краткое описание
└── enterprise_guardrails.py         # Enterprise guardrails
```

---

## ✅ Правила импортов для Cognitive Agent

### Разрешено:

```python
# ✅ Импорт из сервисов (apps/)
from apps.decision_engine.src.decision_engine import DecisionEngine
from apps.job_automation_agent.job_agent import process_request_sync
from apps.it_compass.src.it_compass_scanner import get_scanner

# ✅ Импорт из атомов (src/)
from src.security.rate_limiter import RateLimiter
from src.security.secret_manager import SecretManager
from src.security.secure_path import SecurePath
from src.ai.config import ConfigManager
from src.code_analyzer import CodeAnalyzer
from src.documentation_analyzer import DocumentationAnalyzer
from src.test_analyzer import TestAnalyzer

# ✅ Импорт из других модулей агента
from .base_agent import BaseCognitiveAgent
```

### ЗАПРЕЩЕНО:

```python
# ❌ НЕЛЬЗЯ - не импортировать из других агентов
from agents.other_agent.src.module import Something

# ❌ НЕЛЬЗЯ - не импортировать из атомов, если есть сервис-аналог
from src.some_atom import Something  # Используйте сервис вместо атома

# ❌ НЕЛЬЗЯ - не импортировать из агентов в атомы (это нарушает архитектуру)
# (Это правило для атомов, но важно помнить)
```

---

## 🔒 Безопасность (ОБЯЗАТЕЛЬНО)

### Все операции с файлами должны проходить через SecurePath:

```python
# ✅ Правильно
from src.security.secure_path import SecurePath

secure_path = SecurePath(self.project_path)
safe_path = secure_path.resolve(user_input)
```

### Все операции с AI должны проходить через rate limiter:

```python
# ✅ Правильно
from src.security.rate_limiter import RateLimiter

self.ai_rate_limiter = PredefinedRateLimiters.ai_calls()
self.ai_rate_limiter.check_rate_limit(f"ai:{self.agent_id}")
```

### Все операции с секретами должны проходить через SecretManager:

```python
# ✅ Правильно
from src.security.secret_manager import SecretManager

self.secret_manager = SecretManager(project_root=self.project_path)
secret = self.secret_manager.get_secret("API_KEY")
```

### Все входные данные должны валидироваться:

```python
# ✅ Правильно
self._validate_task(task)
self._validate_ai_response(response)
```

---

## 🎯 Принципы работы Cognitive Agent

### 1. Самостоятельное сканирование

Агент должен сканировать проект самостоятельно, используя навыки:

- `project-scanner` — для сканирования файлов
- `code-security-auditor` — для аудита безопасности
- `task-planner` — для планирования действий

### 2. AI-оркестрация

Агент использует AI для:
- Генерации рекомендаций
- Планирования задач
- Анализа кода и документации

### 3. Самообучение через RAG

Агент обучается на основе:
- Анализа выполненных задач
- Обратной связи от пользователя
- Хранения истории в RAG-системе

---

## 🧪 Тестирование

### Обязательные тесты для Cognitive Agent:

```bash
# Запуск тестов безопасности
pytest agents/cognitive_agent/tests/test_rate_limiter.py
pytest agents/cognitive_agent/tests/test_secret_manager.py
pytest agents/cognitive_agent/tests/test_secure_path.py
pytest agents/cognitive_agent/tests/test_enterprise_guardrails.py

# Запуск всех тестов агента
pytest agents/cognitive_agent/tests/
```

---

## 🚀 Запуск Cognitive Agent

```bash
# Из корня проекта
cd agents/cognitive_agent
python -m src.base_agent

# Или запустить основной агент
python agents/cognitive_agent/autonomous_agent.py
```

---

## 📝 Документация

Каждый раз при изменении архитектуры агента:

1. Обновите `AGENT_DOCUMENTATION.md`
2. Добавьте отчёт в `docs/`
3. Обновите `README.md`
4. Создайте ADR в `docs/architecture/decisions/` если меняете ключевую архитектуру

---

## 🔄 Миграции и рефакторинг

### При перемещении модулей из агентов в атомы:

1. Скопируйте модуль в `src/`
2. Обновите импорты во всех файлах
3. Удалите модуль из агентов
4. Обновите документацию
5. Создайте ADR

### Пример миграции:

```python
# Было (в агентах)
from agents.cognitive_agent.security.rate_limiter import RateLimiter

# Стало (в атомах)
from src.security.rate_limiter import RateLimiter
```

---

## 📚 Связанные документы

- [`docs/architecture/ai-developer-rules.md`](../../docs/architecture/ai-developer-rules.md) — Общие правила архитектуры
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md) — Общая архитектура проекта
- [`.ai-context.md`](../../.ai-context.md) — Контекст автора
- [`AGENT_DOCUMENTATION.md`](AGENT_DOCUMENTATION.md) — Полная документация агента

---

*Последнее обновление: 2026-06-27*
*Версия: 2.0*
*Статус: Актуально*
