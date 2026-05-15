# MCP Server для Portfolio System Architect

MCP (Model Control Protocol) сервер для интеграции с ИИ-агентами. Предоставляет инструменты для работы с проектом, IT-Compass, RAG системой и профессиональным контекстом.

## 🎯 Назначение

Сервер предоставляет 12 инструментов для ИИ-агентов через MCP протокол (stdio транспорт):

- 📂 **Чтение файлов** — доступ к любому файлу проекта
- 🔍 **Поиск** — поиск текста в файлах
- 📊 **Анализ структуры** — обзор директорий и файлов
- 🧠 **IT-Compass** — доступ к маркерам компетенций
- 🤖 **RAG статус** — проверка состояния RAG системы
- 📈 **Health checks** — проверка здоровья проекта

## 🏗️ Архитектура

```
┌─────────────────────┐
│   AI Agent          │
│   (Claude, etc.)    │
└──────────┬──────────┘
           │ MCP Protocol
           │ (stdio)
           ▼
┌─────────────────────┐
│   mcp_server.py     │
│   (Portfolio MCP)   │
└──────────┬──────────┘
           │
    ┌──────┴──────────────┬──────────────┬─────────────┐
    │                     │              │             │
    ▼                     ▼              ▼             ▼
┌─────────┐       ┌──────────┐   ┌──────────┐  ┌──────────┐
│ Project │       │ IT-Compass│  │   RAG    │  │  Files   │
│ Context │       │  Domains │   │  Status  │  │  System  │
└─────────┘       └──────────┘   └──────────┘  └──────────┘
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd tools/ai_integration
pip install mcp pydantic
```

### 2. Запуск сервера

```bash
# Из корня проекта
python tools/ai_integration/mcp_server.py
```

Сервер запустится в режиме **stdio** (стандартный ввод/вывод) для интеграции с ИИ-агентами.

### 3. Интеграция с ИИ-агентом

#### Для Claude Desktop:

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["tools/ai_integration/mcp_server.py"],
      "cwd": "/path/to/portfolio-system-architect"
    }
  }
}
```

#### Для VS Code (Continue):

Добавьте в `mcp.json`:

```json
{
  "mcpServers": {
    "portfolio": {
      "command": "python",
      "args": ["tools/ai_integration/mcp_server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## 🛠️ Инструменты

### 1. `get_project_context()`

Получить контекст проекта (название, автор, компоненты).

**Response:**
```json
{
  "name": "portfolio-system-architect",
  "author": "Ekaterina Kudelya",
  "description": "Когнитивная архитектура для системного мышления",
  "components": [
    "IT-Compass",
    "RAG System",
    "System Thinking Markers",
    "Portfolio Organizer",
    "Decision Engine",
    "Career Development"
  ]
}
```

### 2. `read_ai_context()`

Прочитать файл `.ai-context.md`.

**Response:** Содержимое файла `.ai-context.md`.

### 3. `list_it_compass_domains()`

Получить список доменов IT-Compass.

**Response:**
```json
{
  "domains": [
    "apps/it-compass/system_thinking_markers.json",
    "apps/it-compass/career_development_markers.json"
  ]
}
```

### 4. `get_professional_journey()`

Получить профессиональный путь автора.

**Response:** Содержимое `docs/professional-journey/README.md`.

### 5. `list_project_files(directory)`

Список файлов в директории.

**Параметры:**
- `directory` (str, default=".") — путь к директории

**Response:**
```json
{
  "directory": ".",
  "files": [
    {"name": "README.md", "type": "file", "size": 1234},
    {"name": "apps", "type": "directory", "size": 0}
  ]
}
```

### 6. `check_project_health()`

Проверить здоровье проекта.

**Response:**
```json
{
  "health_checks": [
    {"file": ".ai-context.md", "exists": true, "size": 500},
    {"file": "pyproject.toml", "exists": true, "size": 2000},
    {"file": "FastAPI", "status": "OK", "version": "0.136.1"}
  ]
}
```

### 7. `read_project_file(path)`

Прочитать любой файл проекта.

**Параметры:**
- `path` (str) — путь к файлу

**Response:** Содержимое файла.

### 8. `get_system_thinking_markers()`

Получить маркеры системного мышления.

**Response:**
```json
{
  "system_thinking_markers": [
    {
      "file": "apps/it-compass/system_thinking_markers.json",
      "markers_count": 15
    }
  ]
}
```

### 9. `get_rag_status()`

Получить статус RAG системы.

**Response:**
```json
{
  "rag_system_status": {
    "apps/decision-engine": {
      "exists": true,
      "file_count": 25,
      "has_docker": true
    },
    "chroma_db": {
      "exists": true,
      "is_dir": true
    }
  }
}
```

### 10. `search_in_project(query, file_pattern)`

Поиск текста в файлах проекта.

**Параметры:**
- `query` (str) — строка для поиска
- `file_pattern` (str, default="*.py") — шаблон файлов

**Response:**
```json
{
  "query": "def analyze",
  "file_pattern": "*.py",
  "results_count": 15,
  "results": [
    {"file": "src/analysis.py", "matches": 3},
    {"file": "apps/decision_engine/core.py", "matches": 1}
  ]
}
```

### 11. `get_service_status(service)`

Получить статус сервисов проекта.

**Параметры:**
- `service` (str, default="all") — имя сервиса или "all"

**Response:**
```json
{
  "services_status": {
    "gateway": {
      "exists": true,
      "description": "API Gateway для маршрутизации запросов",
      "file_count": 5,
      "files_sample": [{"name": "main.py", "size": 1500}]
    }
  }
}
```

### 12. `analyze_project_structure()`

Анализ структуры проекта.

**Response:**
```json
{
  "project_structure": {
    "apps": {
      "item_count": 12,
      "items": [{"name": "auth_service", "type": "dir"}]
    },
    "docs": {
      "item_count": 50,
      "items": [{"name": "README.md", "type": "file"}]
    }
  },
  "file_types": {
    ".py": 250,
    ".md": 100,
    ".json": 50
  }
}
```

## 🧪 Тестирование

### Запуск тестов

```bash
cd tools/ai_integration
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Пример теста

```python
def test_get_project_context(mcp_client):
    result = mcp_client.call_tool("get_project_context", {})
    assert "name" in result
    assert result["name"] == "portfolio-system-architect"
```

## 🐳 Docker-развёртывание

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY tools/ai_integration/ .
COPY pyproject.toml .

RUN pip install mcp pydantic

CMD ["python", "mcp_server.py"]
```

### docker-compose.yml

```yaml
services:
  mcp-server:
    build:
      context: .
      dockerfile: tools/ai_integration/Dockerfile
    volumes:
      - .:/app
    stdin_open: true
    tty: true
```

## 🛠️ Troubleshooting

### Ошибка: "MCP библиотека не установлена"

**Решение:**
```bash
pip install mcp
```

### Ошибка: "Не найден .ai-context.md"

**Решение:** Создайте файл `.ai-context.md` в корне проекта.

### Ошибка: "MCP протокол не поддерживается"

**Решение:** Убедитесь, что ИИ-агент поддерживает MCP (Claude Desktop, Continue IDE).

## 📊 Метрики

### Тесты

- **Количество:** ≥25 тестов
- **Покрытие:** ≥75%
- **Прохождение:** 100%

### Производительность

- **Latency:** ~50ms на инструмент
- **Throughput:** ~20 запросов/сек
- **Memory:** ~50MB

## 🤝 Вклад

1. Добавьте новый инструмент для специфичной задачи
2. Напишите тесты для инструмента
3. Обновите документацию
4. Отправьте PR

## 📝 История изменений

### v0.1.0 (2026-05-16)
- ✨ Первоначальная реализация
- 🔧 12 инструментов
- 📡 MCP протокол (stdio)
- 🧪 Базовые тесты

---

*Документация создана: 16 мая 2026 г.*
