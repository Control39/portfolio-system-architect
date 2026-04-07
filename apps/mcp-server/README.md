# MCP Server for Career Autopilot

MCP (Model Context Protocol) сервер с полным доступом к файловой системе, интеграцией с IT-Compass и автоматическим обнаружением маркеров.

## Назначение

Сервер предоставляет инструменты для:
- Чтения/записи файлов в проекте
- Выполнения команд через subprocess
- Доступа к Git (коммиты, история)
- Интеграции с IT-Compass маркерами
- Навигации по репозиторию для разных аудиторий
- Автоматического обнаружения маркеров из коммитов

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

## Быстрый старт

```bash
# Установка зависимостей
cd apps/mcp-server
pip install -r requirements.txt

# Запуск сервера
python src/main.py

# Тестирование с Claude Desktop
# Добавить в конфигурацию Claude Desktop:
# "mcpServers": {
#   "career-autopilot": {
#     "command": "python",
#     "args": ["/path/to/apps/mcp-server/src/main.py"]
#   }
# }
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