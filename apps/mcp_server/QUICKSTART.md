# MCP Server Quick Start Guide

## 📋 Что такое MCP Server?

MCP (Model Context Protocol) сервер предоставляет AI-ассистентам (Koda, Claude, SourceCraft) доступ к инструментам и данным вашего проекта.

## 🎯 Возможности

### 7 групп инструментов:

1. **File Tools** - работа с файлами
2. **Git Tools** - Git операции
3. **IT-Compass Tools** - маркеры компетенций
4. **ChromaDB Tools** - векторный поиск
5. **Monitoring Tools** - Prometheus, Grafana
6. **App Management** - 12 микросервисов
7. **Security Tools** - bandit, pip-audit

### 2 типа ресурсов:

1. **Navigation** - навигация по проекту для разных аудиторий
2. **IT-Compass** - информация о доменах компетенций

---

## 🚀 Установка и запуск

### Вариант 1: Локальный запуск (рекомендуется для разработки)

```powershell
# Переход в директорию MCP сервера
cd apps/mcp-server

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python src/main.py
```

**Ожидаемый вывод:**
```
🚀 Career Autopilot MCP Server
   Project root: C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect
   IT-Compass path: .../apps/it-compass/src/data/markers
   ChromaDB path: .../chroma_data
   Monitoring path: .../monitoring
✅ File tools initialized
✅ Git tools initialized
✅ IT-Compass tools initialized
✅ ChromaDB tools initialized
✅ Monitoring tools initialized
============================================================
✅ Career Autopilot MCP Server Ready
============================================================
```

### Вариант 2: Docker запуск

```powershell
# Сборка образа
docker build -t career-autopilot-mcp:latest .

# Запуск контейнера
docker run -it --rm `
  -v ${PWD}/../..:/workspace `
  -v portfolio-mcp-data:/app/data `
  career-autopilot-mcp:latest
```

---

## 🔌 Интеграция с AI-ассистентами

### Claude Desktop

**Windows:** Откройте `%APPDATA%\Claude\claude_desktop_config.json`

Добавьте конфигурацию:

```json
{
  "mcpServers": {
    "career-autopilot": {
      "command": "python",
      "args": [
        "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/apps/mcp-server/src/main.py"
      ],
      "cwd": "C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/apps/mcp-server"
    }
  }
}
```

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "career-autopilot": {
      "command": "python",
      "args": [
        "/Users/username/DeveloperEnvironment/projects/portfolio-system-architect/apps/mcp-server/src/main.py"
      ]
    }
  }
}
```

После добавления конфигурации **перезапустите Claude Desktop**.

### Koda AI Assistant

Koda автоматически обнаружит MCP сервер при наличии файла `mcp-config.json`:

```json
{
  "mcpServers": {
    "career-autopilot": {
      "command": "python",
      "args": ["path/to/apps/mcp-server/src/main.py"]
    }
  }
}
```

### VS Code (Cline, Roo Code)

1. Откройте настройки расширения
2. Найдите секцию "MCP Servers"
3. Добавьте новый сервер:

```json
{
  "name": "Career Autopilot",
  "type": "stdio",
  "command": "python",
  "args": ["path/to/apps/mcp-server/src/main.py"]
}
```

---

## 📚 Примеры использования

### 1. Работа с файлами

**Запрос AI:** "Прочитай файл apps/mcp-server/src/main.py"

AI использует инструмент `read_file` для чтения содержимого.

### 2. IT-Compass маркеры

**Запрос AI:** "Покажи маркеры для domain=python, level=3"

AI использует:
```python
evaluate_by_compass(domain="python", level=3)
```

### 3. Векторный поиск

**Запрос AI:** "Найди документы про архитектуру в ChromaDB"

AI использует:
```python
chroma_query(collection="documents", query_text="архитектура", n_results=5)
```

### 4. Мониторинг

**Запрос AI:** "Проверь статус Prometheus и Grafana"

AI использует:
```python
check_monitoring_stack_status()
get_docker_container_stats()
```

### 5. Безопасность

**Запрос AI:** "Запусти сканирование безопасности кода"

AI использует:
```python
run_security_scan(scan_type="bandit")
```

### 6. Навигация по проекту

**Запрос AI:** "Покажи тур по проекту для HR"

AI использует ресурс:
```
navigate://hr
```

Возвращает структурированный тур по ключевым файлам для HR.

---

## 🛠️ Доступные инструменты

### File Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `read_file` | Чтение файла | `path: str` |
| `write_file` | Запись файла | `path: str, content: str` |
| `list_files` | Список файлов | `path: str, recursive: bool` |
| `search_files` | Поиск файлов | `query: str, pattern: str` |

### Git Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `get_git_status` | Статус репозитория | - |
| `get_git_history` | История коммитов | `days: int` |
| `scan_commits_for_markers` | Анализ на маркеры | `commits_count: int` |

### IT-Compass Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `evaluate_by_compass` | Оценка по домену | `domain: str, level: int` |
| `get_markers_by_domain` | Маркеры домена | `domain: str` |
| `get_available_domains` | Список доменов | - |
| `auto_detect_markers_from_code` | Авто-обнаружение | `code_path: str` |

### ChromaDB Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `chroma_get_collections` | Список коллекций | - |
| `chroma_query` | Векторный поиск | `collection, query, n_results` |
| `chroma_add_document` | Добавление документа | `collection, document, metadata` |
| `chroma_get_collection_info` | Информация | `collection: str` |

### Monitoring Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `get_prometheus_targets` | Target'ы Prometheus | - |
| `get_prometheus_metrics` | PromQL запрос | `query: str` |
| `get_grafana_dashboards` | Дашборды Grafana | - |
| `check_monitoring_stack_status` | Статус стека | - |
| `get_docker_container_stats` | Статистика Docker | - |

### App Management

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `list_apps` | Список приложений | - |
| `get_app_info` | Информация о приложении | `app_name: str` |
| `restart_app` | Перезапуск | `app_name: str` |

### Security Tools

| Инструмент | Описание | Параметры |
|------------|----------|-----------|
| `run_security_scan` | Сканирование | `scan_type: str` |

---

## 🔧 Настройка

### Переменные окружения

Создайте файл `.env` в директории `apps/mcp-server`:

```env
# Проект
PROJECT_ROOT=C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect

# ChromaDB
CHROMA_DB_PATH=C:/Users/Z/DeveloperEnvironment/projects/portfolio-system-architect/chroma_data

# Мониторинг
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# Git
GIT_EMAIL=your.email@example.com
GIT_NAME=Your Name
```

---

## 🐛 Troubleshooting

### Ошибка: "ModuleNotFoundError: No module named 'fastmcp'"

**Решение:**
```powershell
pip install -r requirements.txt
```

### Ошибка: "IT-Compass markers path not found"

**Решение:** Проверьте что `apps/it-compass/src/data/markers/` существует и содержит JSON файлы.

### Ошибка: "ChromaDB not available"

**Решение:**
1. Убедитесь что chromadb установлен: `pip install chromadb`
2. Проверьте путь к данным: `CHROMA_DB_PATH`

### Ошибка: "Prometheus not available"

**Решение:**
1. Запустите стек мониторинга: `docker-compose up prometheus grafana`
2. Проверьте что Prometheus доступен на `http://localhost:9090`

---

## 📖 Дополнительная документация

- [README.md](README.md) - полная документация
- [mcp-config.json](mcp-config.json) - конфигурация MCP
- [Dockerfile](Dockerfile) - сборка Docker образа

---

## 🎯 Сценарии использования

### Для разработки

```python
# AI помогает с кодом
- read_file("src/main.py")
- write_file("src/new_feature.py", content)
- run_security_scan("bandit")
```

### Для документации

```python
# AI генерирует документацию
- get_navigation_resource("tech_lead")
- evaluate_by_compass("python", 3)
- list_files("docs/", recursive=True)
```

### Для мониторинга

```python
# AI проверяет состояние системы
- check_monitoring_stack_status()
- get_docker_container_stats()
- get_prometheus_metrics("up")
```

### Для безопасности

```python
# AI сканирует уязвимости
- run_security_scan("bandit")
- run_security_scan("pip-audit")
- get_git_history(7)  # коммиты за неделю
```

---

**Готово!** 🎉 MCP сервер настроен и готов к работе с AI-ассистентами.
