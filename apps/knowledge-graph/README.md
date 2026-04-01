# Knowledge Graph Service

Сервис графа знаний для экосистемы portfolio-system-architect.

## 🎯 Цель

Извлекать сущности (технологии, проекты, люди, навыки) из документов проекта и строить семантические связи между ними.

## 🚀 Быстрый старт

### Локальный запуск
```bash
# Установка зависимостей
pip install -r requirements.txt

# Загрузка модели spaCy для русского языка
python -m spacy download ru_core_news_sm

# Запуск сервиса
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8100
```

### Запуск через Docker
```bash
docker build -t knowledge-graph .
docker run -p 8100:8000 knowledge-graph
```

## 📚 API Endpoints

### GET /health
Проверка здоровья сервиса

### POST /graph/entities/extract
Извлечение сущностей из текста

### POST /graph/entities/add
Добавление сущностей в граф

### GET /graph/entities
Получение всех сущностей

### GET /graph/entities/{entity_id}
Получение информации о сущности

### POST /graph/relationships
Создание связей между сущностями

### GET /graph/query
Запросы к графу знаний

## 🏗️ Архитектура

```
src/
├── api/           # FastAPI endpoints
├── core/          # Логика графа знаний
├── models/        # Pydantic модели
└── utils/         # Вспомогательные функции
```

## 🔧 Конфигурация

Создайте файл `.env` в корневой директории:
```env
KNOWLEDGE_GRAPH_HOST=0.0.0.0
KNOWLEDGE_GRAPH_PORT=8100
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
SPACY_MODEL=ru_core_news_sm
```

## 🧪 Тестирование
```bash
# Запуск тестов
pytest tests/

# Запуск с покрытием
pytest --cov=src tests/
```

## 🔄 Интеграция

Сервис интегрируется с:
- **Architect Assistant** - улучшение RAG поиска через граф знаний
- **Unified API Gateway** - единая точка входа
- **Learning Feedback Loop** - обновление графа на основе feedback

