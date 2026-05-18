# Стандарт структуры сервиса

> **Версия:** 1.0.0  
> **Дата:** 18 мая 2026 г.  
> **Применимость:** Все сервисы в `apps/`

---

## 🎯 Цели стандарта

1. **Единый入口** — каждый сервис имеет `main.py` или `app.py`
2. **Чёткое разделение** — `src/` для кода, `tests/` для тестов, `config/` для конфигов
3. **Docker-ready** — каждый сервис имеет `Dockerfile`
4. **Тестирование** — минимальное покрытие 85%
5. **Документация** — `README.md` с API, deployment, contributing

---

## 📁 Стандартная структура

```
<service-name>/
├── main.py                 # Entry point (FastAPI/Flask app)
├── README.md              # Документация (7 обязательных секций)
├── requirements.txt       # Зависимости
├── Dockerfile            # Контейнеризация (python:3.11-slim)
├── .dockerignore         # Исключения для Docker
├── .gitignore            # Исключения для Git
│
├── src/                  # Исходный код
│   ├── __init__.py
│   ├── core/            # Ядро сервиса
│   ├── api/             # API endpoints (если FastAPI)
│   └── utils/           # Вспомогательные функции
│
├── tests/               # Тесты
│   ├── __init__.py
│   ├── test_core.py    # Юнит-тесты
│   └── test_api.py     # Интеграционные тесты
│
├── config/              # Конфигурации (опционально)
│   ├── config.yaml
│   └── settings.py
│
└── docs/                # Документация (опционально)
    ├── architecture.md
    └── api.md
```

---

## 📋 Обязательные файлы

### 1. main.py (Entry Point)

```python
"""
<service-name> — краткое описание

API:
    GET /health — проверка здоровья
    GET / — информация о сервисе
"""

from fastapi import FastAPI

app = FastAPI(
    title="<service-name>",
    description="<краткое описание>",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy", "service": "<service-name>"}


@app.get("/")
async def root():
    """Основная информация о сервисе."""
    return {
        "name": "<service-name>",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. README.md (7 обязательных секций)

```markdown
# <Service Name>

## Purpose
<Цель сервиса>

## Features
- <Функция 1>
- <Функция 2>

## API
| Endpoint | Method | Описание |
|----------|--------|----------|
| /health | GET | Проверка здоровья |
| / | GET | Информация о сервисе |

## Dependencies
```bash
pip install -r requirements.txt
```

## Deployment
```bash
docker build -t <service-name> .
docker run -p 8000:8000 <service-name>
```

## Contributing
См. [CONTRIBUTING.md](../../CONTRIBUTING.md)
```

### 3. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. requirements.txt

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pytest>=7.0.0
```

---

## 🧪 Стандарт тестирования

```
tests/
├── __init__.py
├── conftest.py          # Общие fixtures
├── test_<module>.py     # Юнит-тесты
└── test_api.py          # API тесты
```

**Пример теста:**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## 🔍 Проверка соответствия

### Обязательные файлы (check_readme_quality.py)

| Файл | Проверка | Критично |
|------|----------|----------|
| main.py/app.py | Entry point существует | ✅ |
| README.md | 7 секций | ✅ |
| requirements.txt | Зависимости | ✅ |
| Dockerfile | Контейнеризация | ✅ |
| tests/ | Тесты | ✅ |

### Опциональные файлы

| Файл | Когда нужен |
|------|-------------|
| config/ | Если есть конфигурация |
| docs/ | Если сложная документация |
| scripts/ | Если есть скрипты |
| examples/ | Если есть примеры использования |

---

## 🛠️ Инструменты унификации

### auto-standardize.py

```python
#!/usr/bin/env python
"""
Автоматическая стандартизация структуры сервиса.

Использование:
    python auto-standardize.py <service-name>
"""

import os
import shutil
from pathlib import Path


def create_standard_structure(service_name: str, base_path: Path):
    """Создать стандартную структуру сервиса."""
    service_path = base_path / service_name
    
    # Проверка существования
    if service_path.exists():
        print(f"⚠️  Сервис {service_name} уже существует")
        return
    
    # Создание директорий
    (service_path / "src").mkdir(parents=True)
    (service_path / "tests").mkdir(parents=True)
    (service_path / "src" / "core").mkdir()
    (service_path / "src" / "api").mkdir()
    
    # Создание файлов
    (service_path / "__init__.py").touch()
    (service_path / "src" / "__init__.py").touch()
    (service_path / "tests" / "__init__.py").touch()
    
    print(f"✅ Создана стандартная структура для {service_name}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python auto-standardize.py <service-name>")
        sys.exit(1)
    
    service_name = sys.argv[1]
    base_path = Path(__file__).parent / "apps"
    create_standard_structure(service_name, base_path)
```

---

## 📊 Метрики стандартизации

| Показатель | Цель | Текущее |
|------------|------|---------|
| Сервисов с main.py | 100% | TBD |
| Сервисов с Dockerfile | 100% | TBD |
| Сервисов с README (7 секций) | 100% | 73% (11/15) |
| Сервисов с tests/ | 100% | TBD |

---

## 🔄 План миграции

### Phase 1: Анализ (1 день)

- [ ] Провести аудит всех сервисов
- [ ] Составить матрицу соответствия
- [ ] Приоритизировать сервисы для миграции

### Phase 2: Шаблон (2 дня)

- [ ] Создать `template-service` как эталон
- [ ] Написать `auto-standardize.py`
- [ ] Протестировать на тестовом сервисе

### Phase 3: Миграция (3-5 дней)

- [ ] Мигрировать 5 приоритетных сервисов
- [ ] Протестировать каждый
- [ ] Обновить docker-compose.yml

### Phase 4: Автоматизация (1 день)

- [ ] Добавить pre-commit hook для проверки
- [ ] CI/CD проверка структуры
- [ ] Документация для новых сервисов

---

## ✅ Чеклист для новых сервисов

Создавая новый сервис, убедись:

- [ ] Создан `main.py` с FastAPI app
- [ ] Создан `README.md` с 7 секциями
- [ ] Создан `requirements.txt`
- [ ] Создан `Dockerfile`
- [ ] Созданы `src/` и `tests/`
- [ ] Добавлен в `docker-compose.yml`
- [ ] Написаны базовые тесты
- [ ] Проходит `make lint` и `make test`

---

*Последнее обновление: 18 мая 2026 г.*
