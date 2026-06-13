# Архитектура Cognitive Agent

## 🧬 Принципы Композиционной Архитектуры

Cognitive Agent следует принципу **«Атомы и Молекулы»**:

### **Атомы (src/)**
Переиспользуемые компоненты в корне проекта:

```
src/
├── ai/                        # 🧠 AI интеграции
│   ├── gigachat_bridge.py     # GigaChat + LangChain
│   └── __init__.py
├── shared/                    # 📦 Общие компоненты
│   ├── models.py              # Pydantic схемы
│   └── __init__.py
└── core/                      # ⚙️ Базовые утилиты
    ├── config_loader.py       # Загрузчик конфигов
    └── __init__.py
```

**Правило:** Атомы НЕ зависят от конкретных сервисов. Они могут использоваться любым сервисом.

---

### **Молекулы (apps/cognitive_agent/)**
Конкретный сервис, собирающий атомы:

```
apps/cognitive_agent/
├── src/                       # Точка входа сервиса
│   ├── main.py                # FastAPI сервер
│   └── api/
│       └── endpoints.py       # API эндпоинты
├── scripts/                   # Скрипты агента
│   ├── scanner_main.py        # Сканирование
│   ├── planner_main.py        # Планирование
│   └── learning_main.py       # Обучение
├── config/                    # Конфигурация
└── requirements.txt           # Зависимости
```

**Правило:** Молекулы импортируют атомы из `src/` и добавляют свою бизнес-логику.

---

## 🔄 Как работают импорты

```python
# apps/cognitive_agent/src/api/endpoints.py
from src.ai import GigaMCPBridge      # ← Атом из корневого src/
from src.shared.models import ScanRequest  # ← Атом из корневого src/

# Не так:
# from agents.cognitive_agent.src.ai import ...  # ❌ Неправильно
```

---

## 📋 Что куда помещать

| Компонент | Где создавать | Почему |
|-----------|---------------|--------|
| **GigaChat интеграция** | `src/ai/` | Используется многими сервисами |
| **Pydantic модели** | `src/shared/` | Общие схемы данных |
| **Config loader** | `src/core/` | Базовая утилита |
| **FastAPI сервер** | `apps/cognitive_agent/src/` | Конкретный сервис |
| **API эндпоинты** | `apps/cognitive_agent/src/api/` | Конкретный сервис |
| **Скрипты агента** | `apps/cognitive_agent/scripts/` | Бизнес-логика сервиса |

---

## 🚀 Быстрый старт

### Запуск локально:

```bash
cd apps/cognitive_agent
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8008
```

### Запуск через Docker:

```bash
docker-compose up -d cognitive-agent
```

---

## 📊 Структура проекта

```
portfolio-system-architect/
├── src/                          # 🧬 АТОМЫ
│   ├── ai/                       # LLM интеграции
│   ├── shared/                   # Общие схемы
│   └── core/                     # Базовые утилиты
│
├── apps/                         # 🧪 МОЛЕКУЛЫ
│   ├── cognitive_agent/          # Когнитивный агент
│   │   ├── src/                  # FastAPI сервер
│   │   ├── scripts/              # Скрипты агента
│   │   └── config/               # Конфигурация
│   ├── decision_engine/          # Другой сервис
│   └── ...
│
└── docs/                         # 📚 Документация
    ├── COGNITIVE_AGENT_ARCHITECTURE.md
    └── ...
```

---

## ⚠️ Важные правила

1. **Никогда не удаляй файлы из `src/` без проверки** — это атомы, они могут использоваться другими сервисами
2. **Перед добавлением кода в сервис** — проверь, нельзя ли вынести его в атом
3. **Импорты всегда из корневого `src/`** — не импортируй из других сервисов напрямую

---

**Версия:** 0.1.0
**Дата:** 5 июня 2026
**Автор:** Екатерина Куделя (@Control39)
