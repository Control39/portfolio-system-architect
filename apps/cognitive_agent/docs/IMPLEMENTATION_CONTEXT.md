# Cognitive Agent: Контекст реализации

> **Для передачи другому ИИ**  
> **Дата создания:** 5 июня 2026  
> **Последнее обновление:** 5 июня 2026  
> **Автор:** Екатерина Куделя (@Control39)

---

## 🎯 **Что такое Cognitive Agent**

**Cognitive Agent** — автономный планировщик задач для автоматизации рабочих процессов.

### **Архитектура:**
```
Scanner → Planner → Skills → Learning System → Reports
   ↓         ↓         ↓          ↓
 Сканирует Планирует Выполняет Анализирует
 проект     задачи    навыки    метрики
```

### **Текущий статус:** MVP + Восстановление (v0.1.0)

---

## ✅ **ЧТО УЖЕ РЕАЛИЗОВАНО (в этом репо)**

| Компонент | Путь | Статус |
|-----------|------|--------|
| **Scanner** | `apps/cognitive_agent/scripts/scanner_main.py` | ✅ 100% |
| **Planner** | `apps/cognitive_agent/scripts/planner_main.py` | ✅ 70% (без ИИ) |
| **Learning** | `apps/cognitive_agent/scripts/learning_main.py` | ✅ 100% |
| **Skills** | `apps/cognitive_agent/scripts/*.py` (16+) | ✅ 100% |
| **Monitoring** | `*-monitor.py`, `alert-system.py` | ✅ 100% |
| **Documentation** | `docs/ARCHITECTURE.md`, `docs/FLOW.md` | ✅ 100% |

---

## ❌ **ЧТО НЕ ХВАТАЕТ (для полной реализации)**

| Компонент | Приоритет | Статус |
|-----------|-----------|--------|
| **FastAPI Server** | 🔥 Высокий | ❌ Нет `main.py` с API |
| **AI Integration** | 🔥 Высокий | ❌ Нет LangChain/GigaChat |
| **Knowledge Graph** | 🟡 Средний | 🟡 Частично в других сервисах |
| **E2E Tests** | 🟡 Средний | ❌ Нет тестов полного цикла |
| **Docker Compose** | 🟡 Средний | ❌ Нет docker-compose.yml |

---

## 🔍 **ГДЕ ИСКАТЬ УЖЕ ГОТОВЫЙ КОД**

### **Локация 1: Текущий репозиторий (portfolio-system-architect)**

```
apps/cognitive_agent/
├── scripts/
│   ├── scanner_main.py      # Сканирование проекта
│   ├── planner_main.py      # Планирование задач
│   ├── learning_main.py     # Система обучения
│   ├── alert-system.py      # Оповещения
│   └── ... (16+ навыков)
```

### **Локация 2: C:\Projects (другие проекты)**

| Компонент | Файл | Путь |
|-----------|------|------|
| **GigaChat API** | `gigachat_api.py` | `C:\Projects\*\gigachat_api.py` |
| **LangChain** | `orchestrator.py` | `C:\Projects\*\orchestrator.py` |
| **LangChain Bridge** | `gigachain_bridge.py` | `C:\Projects\*\gigachain_bridge.py` |
| **Ollama** | `initialization.py` | `C:\Projects\*\initialization.py` |
| **ChromaDB** | `entities.py` | `C:\Projects\*\entities.py` |
| **Knowledge Graph** | `test_integration_cognitive_agent.py` | `C:\Projects\*\test_integration_cognitive_agent.py` |
| **HuggingFace** | `embeddings.py` | `C:\Projects\*\embeddings.py` |

### **Локация 3: Другие сервисы в этом репо**

| Компонент | Файл | Путь |
|-----------|------|------|
| **Decision Engine** | `apps/decision_engine/core/models.py` | `apps/decision_engine/` |
| **Thought Architecture** | `apps/thought_architecture/src/core/models.py` | `apps/thought_architecture/` |
| **Chat Backend** | `apps/chat_backend/core/room_store/models.py` | `apps/chat_backend/` |

---

## 📂 **РЕЗУЛЬТАТЫ ПОИСКА**

### **Файлы с результатами:**

| Файл | Содержит |
|------|----------|
| `apps/cognitive_agent/search_results_20260605_072937.csv` | Поиск в текущем репо (50 результатов) |
| `C:\Projects\search_results_20260605_073118.csv` | Поиск в C:\Projects (100 результатов) |

### **Ключевые слова для поиска:**

```
gigachat, chromadb, langchain, huggingface, ollama,
vectorstore, embeddings, knowledge_graph, graph_db,
models.py, schemas.py, main.py, app.py, api.py
```

### **Папки для игнорирования при поиске:**

```
.venv, venv, env, __pycache__, .git, node_modules,
.pytest_cache, .mypy_cache, build, dist, .idea, .vscode, bin, obj, packages
```

---

## 🛠️ **СКОПИРОВАТЬ ДЛЯ COGNITIVE AGENT API**

### **1. Атомы (в корневой src/)**

**GigaChat интеграция (скопировать):**
- **Откуда:** `C:\Projects\*\gigachat_api.py` или `C:\Projects\*\gigachain_bridge.py`
- **Куда:** `src/ai/gigachat_bridge.py`
- **Что скопировать:**
  - Импорты: `from langchain_gigachat import GigaChat`
  - Конфигурация API ключа
  - Обработчик ошибок и fallback на Ollama

**Модели данных (скопировать):**
- **Откуда:** Любой файл с Pydantic моделями
- **Куда:** `src/shared/models.py`
- **Что скопировать:**
  - ScanRequest, ScanResponse
  - PlanRequest, PlanResponse
  - ExecuteRequest, ExecuteResponse

**Ollama Fallback (скопировать):**
- **Откуда:** `C:\Projects\*\initialization.py`
- **Куда:** `src/ai/ollama_fallback.py`
- **Что скопировать:**
  - Проверка доступности Ollama
  - Загрузка локальных моделей
  - Конфигурация fallback

**ChromaDB (скопировать):**
- **Откуда:** `C:\Projects\*\entities.py`
- **Куда:** `src/ai/chroma_indexer.py`
- **Что скопировать:**
  - Подключение к ChromaDB
  - Создание collection
  - Методы для search/index

### **2. Молекулы (в apps/cognitive_agent/)**

**FastAPI сервер (создать/исправить):**
```python
# apps/cognitive_agent/src/main.py
from fastapi import FastAPI
from src.ai import GigaMCPBridge
from src.shared.models import ScanRequest

app = FastAPI(title="Cognitive Agent API")
```

**API эндпоинты (создать/исправить):**
```python
# apps/cognitive_agent/src/api/endpoints.py
from fastapi import FastAPI, HTTPException
from src.shared.models import ScanRequest, ScanResponse

app = FastAPI()

@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_project(request: ScanRequest):
    # Интегрировать scanner_main.py
    pass
```

---

## 📋 **ПРИОРИТЕТНЫЙ ПЛАН (1 неделя)**

| День | Задача | Источник кода |
|------|--------|---------------|
| **День 1** | Исправить импорты в FastAPI | Обновить на src.ai, src.shared |
| **День 2** | Интегрировать GigaChat в атом | `C:\Projects\*\gigachat_api.py` → `src/ai/` |
| **День 3** | Интегрировать Ollama fallback | `C:\Projects\*\initialization.py` → `src/ai/` |
| **День 4** | Интегрировать ChromaDB | `C:\Projects\*\entities.py` → `src/ai/` |
| **День 5** | Подключить scanner_main.py | `apps/cognitive_agent/scripts/` |
| **День 6** | Подключить planner_main.py | `apps/cognitive_agent/scripts/` |
| **День 7** | Написать тесты | Создать tests/ |

---

## 🎯 **ЧТО ДЕЛАТЬ С ЭТИМ ДОКУМЕНТОМ**

### **Если передаёшь другому ИИ:**

1. **Дай доступ к этому файлу** (`docs/IMPLEMENTATION_CONTEXT.md`)
2. **Дай доступ к `C:\Projects`** (через поиск по ключевым словам)
3. **Дай доступ к текущему репо** (`portfolio-system-architect`)
4. **Скажи, какую задачу выполнять** (например, "создай FastAPI сервер")

### **Если работаешь самостоятельно:**

1. **Сначала создай FastAPI сервер** (`apps/cognitive_agent/src/main.py`)
2. **Затем скопируй GigaChat интеграцию** из `C:\Projects`
3. **Добавь Ollama fallback** из `C:\Projects`
4. **Подключи ChromaDB** из `C:\Projects`
5. **Напиши тесты** и Docker Compose

---

## 📊 **ТЕКУЩИЕ ФАЙЛЫ В КОММИТЕ**

| Файл | Статус | Описание |
|------|--------|----------|
| `find_implementation.ps1` | ✅ Создан | Скрипт для поиска реализаций |
| `docs/ARCHITECTURE.md` | ✅ Создан | Архитектурные диаграммы |
| `docs/FLOW.md` | ✅ Создан | Поток данных |
| `README.md` | ✅ Обновлён | Диаграммы в README |

---

## 🔗 **ПОЛЕЗНЫЕ ССЫЛКИ**

| Документ | Путь |
|----------|------|
| Архитектура | `docs/ARCHITECTURE.md` |
| Поток данных | `docs/FLOW.md` |
| Основной README | `README.md` |
| Результаты поиска (репо) | `search_results_20260605_072937.csv` |
| Результаты поиска (C:\Projects) | `C:\Projects\search_results_20260605_073118.csv` |

---

## ⚠️ **ВАЖНОЕ ПРИМЕЧАНИЕ**

**Этот агент — не "волшебная кнопка".** Это инструмент, который:
- ✅ Сканирует проект
- ✅ Планирует задачи (без ИИ пока)
- ✅ Выполняет навыки (skills)
- ✅ Собирает метрики
- ❌ **Не генерирует код автоматически**
- ❌ **Не создаёт архитектуру сам**

**Требует настройки и контроля.** Агент — помощник, а не создатель.

---

**Версия документа:** 1.0  
**Дата:** 5 июня 2026  
**Автор:** Екатерина Куделя (@Control39)
