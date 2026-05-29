# Context Builder Service

Сервис для сборки контекста проекта в один файл для передачи LLM 

## Возможности

- ✅ Сканирование проекта с уважением `.gitignore`
- ✅ Определение бинарных файлов
- ✅ Оценка количества токенов (tiktoken)
- ✅ Разбиение на части для больших проектов (chunking)
- ✅ Статистика по файлам и токенам
- ✅ JSON и Markdown вывод
- ✅ Rate limiting
- ✅ Prometheus метрики
- ✅ Graceful shutdown

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness probe |
| GET | `/metrics` | Prometheus метрики |
| GET | `/filter` | Получить настройки фильтрации |
| POST | `/filter` | Обновить настройки |
| POST | `/build` | Собрать контекст (текст) |
| POST | `/build/json` | Собрать контекст (JSON) |
| POST | `/build/chunked` | Собрать с разбиением на части |
| POST | `/build/file` | Сохранить в файл |
| GET | `/structure` | Только структура проекта |

## Быстрый старт

```bash
# Локально
cd apps/context_builder
pip install -r requirements.txt
python main.py

# Docker
docker build -t context-builder .
docker run -p 8600:8600 -v $(pwd):/app context-builder

# Через docker-compose (из корня проекта)
docker-compose up -d context_builder
```

## Примеры запросов

```bash
# Получить структуру проекта
curl "http://localhost:8600/structure?subpath=apps"

# Собрать полный контекст
curl -X POST http://localhost:8600/build \
  -H "Content-Type: application/json" \
  -d '{"paths": ["apps/cognitive_agent"]}'

# Сохранить в файл
curl -X POST http://localhost:8600/build/file \
  -H "Content-Type: application/json" \
  -d '{"paths": ["."]}'

# Разбить на части (если включено)
curl -X POST http://localhost:8600/build/chunked \
  -H "Content-Type: application/json" \
  -d '{"paths": ["."]}'
```

## Переменные окружения

| Variable | Default | Description |
|--------|---------|-------------|
| `CONTEXT_BUILDER_PORT` | `8600` | Порт сервиса |
| `PROJECT_ROOT` | `/app` | Корень проекта |
| `MAX_FILE_SIZE_MB` | `2` | Макс. размер файла |
| `MAX_TOTAL_SIZE_MB` | `10` | Макс. общий размер |
| `ENABLE_CHUNKING` | `false` | Включить разбиение на части |
| `MAX_TOKENS_PER_CHUNK` | `100000` | Токенов на часть |
| `RESPECT_GITIGNORE` | `true` | Учитывать `.gitignore` |
| `DETECT_BINARY` | `true` | Определять бинарные файлы |
| `RATE_LIMIT_ENABLED` | `true` | Включить rate limiting |
