# MCP Server for Career Autopilot

**Версия:** 1.0  
**Статус:** ✅ Готов к использованию

MCP (Model Context Protocol) сервер для работы с экосистемой Career Autopilot и IT-Compass.

## 🎯 Назначение

Сервер предоставляет AI-агентам (Koda, Claude, SourceCraft) доступ к:
- 📁 **Файловой системе** проекта
- 🔀 **Git** и SourceCraft интеграции
- 🧭 **IT-Compass** маркерам компетенций (83 маркера в 19 доменах)
- 🗄️ **ChromaDB** векторному поиску
- 📊 **Мониторингу** (Prometheus, Grafana)
- 🚀 **12 микросервисам** (apps/)
- 🔒 **Безопасности** (bandit, pip-audit)

## 🛠️ Инструменты

### 1. File Tools
- `read_file(path)` - чтение файла
- `write_file(path, content)` - запись файла
- `list_files(path, recursive)` - список файлов
- `search_files(query, pattern)` - поиск файлов

### 2. Git Tools
- `get_git_status()` - статус репозитория
- `get_git_history(days)` - история коммитов
- `scan_commits_for_markers(count)` - анализ коммитов на маркеры
- `get_branch_info()` - информация о ветках

### 3. IT-Compass Tools
- `evaluate_by_compass(domain, level)` - оценка по домену
- `get_markers_by_domain(domain)` - маркеры домена
- `get_available_domains()` - список доменов
- `auto_detect_markers_from_code(path)` - авто-обнаружение маркеров

### 4. ChromaDB Tools
- `chroma_get_collections()` - список коллекций
- `chroma_query(collection, query, n_results)` - векторный поиск
- `chroma_add_document(collection, document, metadata)` - добавление документа
- `chroma_get_collection_info(collection)` - информация о коллекции

### 5. Monitoring Tools
- `get_prometheus_targets()` - target'ы Prometheus
- `get_prometheus_metrics(query)` - PromQL запросы
- `get_grafana_dashboards()` - дашборды Grafana
- `check_monitoring_stack_status()` - статус стека
- `get_docker_container_stats()` - статистика контейнеров

### 6. App Management
- `list_apps()` - список микросервисов
- `get_app_info(app_name)` - информация о приложении
- `restart_app(app_name)` - перезапуск приложения

### 7. Security Tools
- `run_security_scan(scan_type)` - сканирование безопасности
  - `bandit` - статический анализ кода
  - `pip-audit` - проверка уязвимостей зависимостей

## Архитектура

```
apps/mcp-server/
├── src/
│   ├── main.py              # Точка входа FastMCP
│   ├── tools/
│   │   ├── file_tools.py    # Работа с файлами
│   │   ├── git_tools.py     # Работа с Git
│   │   ├── compass_tools.py # Интеграция с IT-Compass
│   │   └── command_tools.py # Выполнение команд
│   ├── resources/
│   │   ├── navigation.py    # Ресурсы навигации
│   │   └── compass.py       # Ресурсы IT-Compass
│   └── utils/
│       └── config.py        # Конфигурация
├── pyproject.toml           # Зависимости
├── Dockerfile               # Контейнеризация
└── requirements.txt         # Python зависимости
```

## Интеграция с экосистемой

- **API Gateway**: регистрируется как сервис в `gateway/config/services.yaml`
- **IT-Compass**: использует маркеры из `apps/it-compass/src/data/markers/`
- **Shared Schemas**: использует контракты из `src/shared/schemas/`
- **Monitoring**: интегрируется с Prometheus через метрики

## 🚀 Быстрый старт

### Локальный запуск

```bash
# Переход в директорию проекта
cd apps/mcp-server

# Установка зависимостей
pip install -e .

# Запуск сервера
python src/main.py
```

### Docker запуск

```bash
# Сборка образа
docker build -t career-autopilot-mcp:latest .

# Запуск контейнера
docker run -it --rm \
  -v $(pwd):/workspace \
  -v portfolio-mcp-data:/app/data \
  career-autopilot-mcp:latest
```

## 🔌 Интеграция с MCP клиентами

### Claude Desktop

Добавьте в конфигурацию Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### Koda / SourceCraft

Используйте готовую конфигурацию из `mcp-config.json`:

```bash
# Копирование конфигурации
cp mcp-config.json ~/.koda/mcp.json
```

### VS Code (Cline, Roo Code)

```json
{
  "mcpServers": [
    {
      "name": "Career Autopilot",
      "type": "stdio",
      "command": "python",
      "args": ["path/to/apps/mcp-server/src/main.py"]
    }
  ]
}
```

## Инструменты

### 1. Файловые операции
- `read_file(path: str) -> str` - чтение файла
- `write_file(path: str, content: str) -> bool` - запись файла
- `list_files(path: str, recursive: bool = False) -> list` - список файлов

### 2. Git операции
- `get_git_status() -> dict` - статус репозитория
- `scan_last_commits_for_markers(commits_count: int = 10) -> str` - анализ коммитов на маркеры
- `get_git_history(days: int = 30) -> list` - история коммитов

### 3. IT-Compass интеграция
- `evaluate_by_compass(domain: str, level: int = None) -> dict` - оценка по домену
- `get_markers_by_domain(domain: str) -> list` - получение маркеров домена
- `auto_detect_markers_from_code() -> list` - автоматическое обнаружение маркеров из кода

### 4. Навигация
- `generate_tour(audience: str) -> str` - генерация тура по репозиторию
- `search_repo(query: str, file_pattern: str = "*.py") -> list` - поиск по репозиторию

### 5. Команды
- `execute_command(command: str, cwd: str = None) -> dict` - выполнение команды
- `run_python_script(script_path: str, args: list = None) -> dict` - запуск Python скрипта

## Конфигурация

Создать `.env` файл:
```env
MCP_HOST=localhost
MCP_PORT=8000
IT_COMPASS_PATH=../it-compass/src/data/markers
PROJECT_ROOT=../..
```

## Развертывание

```bash
# Сборка Docker образа
docker build -t mcp-server:latest .

# Запуск в Docker Compose
docker-compose up mcp-server

# Развертывание в Kubernetes
kubectl apply -f deployment/mcp-server-deployment.yaml
```

## Мониторинг

- Метрики Prometheus: `/metrics`
- Health check: `/health`
- OpenAPI документация: `/docs`

## Лицензия

CC BY-ND 4.0 - как и остальная методология IT-Compass