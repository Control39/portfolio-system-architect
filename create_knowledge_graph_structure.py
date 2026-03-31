#!/usr/bin/env python3
"""
Скрипт для создания структуры Knowledge Graph Service
"""

import os
from pathlib import Path

def create_directory_structure():
    """Создать структуру директорий для Knowledge Graph Service"""
    base_dir = Path("apps/knowledge-graph")
    
    directories = [
        base_dir / "src" / "api",
        base_dir / "src" / "core",
        base_dir / "src" / "models",
        base_dir / "src" / "utils",
        base_dir / "tests",
        base_dir / "data",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана директория: {directory}")
    
    # Создать пустые файлы __init__.py
    init_files = [
        base_dir / "src" / "__init__.py",
        base_dir / "src" / "api" / "__init__.py",
        base_dir / "src" / "core" / "__init__.py",
        base_dir / "src" / "models" / "__init__.py",
        base_dir / "src" / "utils" / "__init__.py",
        base_dir / "tests" / "__init__.py",
    ]
    
    for init_file in init_files:
        init_file.touch(exist_ok=True)
        print(f"✅ Создан файл: {init_file}")
    
    return base_dir

def create_basic_files(base_dir):
    """Создать базовые файлы сервиса"""
    
    # Dockerfile
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/

# Запуск приложения
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""
    
    (base_dir / "Dockerfile").write_text(dockerfile_content)
    print(f"✅ Создан Dockerfile")
    
    # requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
networkx==3.1
spacy==3.7.2
# Для русского языка в spaCy нужно скачать модель: python -m spacy download ru_core_news_sm
python-multipart==0.0.6
httpx==0.25.1
redis==5.0.1
python-dotenv==1.0.0
"""
    
    (base_dir / "requirements.txt").write_text(requirements_content)
    print(f"✅ Создан requirements.txt")
    
    # README.md
    readme_content = """# Knowledge Graph Service

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
"""
    
    (base_dir / "README.md").write_text(readme_content)
    print(f"✅ Создан README.md")
    
    # .env.example
    env_example_content = """# Конфигурация Knowledge Graph Service
KNOWLEDGE_GRAPH_HOST=0.0.0.0
KNOWLEDGE_GRAPH_PORT=8100

# Redis для кэширования
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Модель spaCy для русского языка
SPACY_MODEL=ru_core_news_sm

# Логирование
LOG_LEVEL=INFO
LOG_FORMAT=json

# Граф знаний
GRAPH_STORAGE_TYPE=memory  # memory, redis, neo4j
MAX_ENTITIES=10000
MAX_RELATIONSHIPS=50000
"""
    
    (base_dir / ".env.example").write_text(env_example_content)
    print(f"✅ Создан .env.example")

if __name__ == "__main__":
    print("🚀 Создание структуры Knowledge Graph Service...")
    base_dir = create_directory_structure()
    create_basic_files(base_dir)
    print("✅ Структура Knowledge Graph Service успешно создана!")