#!/usr/bin/env python
"""
Генератор новых сервисов из template-service.

Использование:
    python create_service.py <service-name> [--description "Описание"]
    python create_service.py my-new-service --description "Мой новый сервис"
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


def sanitize_name(name: str) -> str:
    """Преобразовать имя сервиса в валидный формат."""
    # Заменить пробелы на дефисы
    name = name.replace(" ", "-")
    # Привести к нижнему регистру
    name = name.lower()
    # Убрать специальные символы
    name = "".join(c if c.isalnum() or c == "-" else "" for c in name)
    return name


def create_service(service_name: str, description: str, base_path: Path) -> Path:
    """Создать новый сервис из шаблона."""
    sanitized_name = sanitize_name(service_name)
    service_path = base_path / sanitized_name
    
    if service_path.exists():
        print(f"❌ Ошибка: Сервис '{sanitized_name}' уже существует")
        return None
    
    # Шаблоны файлов
    templates = {
        "main.py": f'''"""
{sanitized_name} — {description}

API:
    GET /health — проверка здоровья
    GET / — информация о сервисе
"""

from fastapi import FastAPI

app = FastAPI(
    title="{sanitized_name.replace("-", " ").title()}",
    description="{description}",
    version="1.0.0"
)


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {{"status": "healthy", "service": "{sanitized_name}"}}


@app.get("/")
async def root():
    """Основная информация о сервисе."""
    return {{
        "name": "{sanitized_name}",
        "description": "{description}",
        "version": "1.0.0",
        "docs": "/docs"
    }}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        
        "README.md": f'''# {sanitized_name.replace("-", " ").title()}

## Purpose
{description}

## Features
- Основная функция 1
- Основая функция 2
- Интеграция с другими сервисами

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
docker build -t {sanitized_name} .
docker run -p 8000:8000 {sanitized_name}
```

## Contributing
См. [CONTRIBUTING.md](../../CONTRIBUTING.md)
''',
        
        "requirements.txt": """fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pytest>=7.0.0
""",
        
        "Dockerfile": f"""FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
        
        ".dockerignore": """__pycache__
*.pyc
*.pyo
*.pyd
.Python
.env
.venv
env
venv
.venv
.git
.gitignore
*.md
.vscode
.idea
__pycache__
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
""",
        
        ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
.env
.eggs/
*.egg-info/
.dist/
build/
develop-eggs/
downloads/
eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.tox/
.nox/
""",
    }
    
    # Шаблоны директорий
    dirs = ["src", "src/core", "src/api", "tests"]
    
    # Создание директорий
    print(f"📁 Создание директорий для {sanitized_name}...")
    for dir_path in dirs:
        (service_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Создание __init__.py
    (service_path / "__init__.py").touch()
    (service_path / "src" / "__init__.py").touch()
    (service_path / "src" / "core" / "__init__.py").touch()
    (service_path / "src" / "api" / "__init__.py").touch()
    (service_path / "tests" / "__init__.py").touch()
    
    # Создание файлов
    print(f"📝 Создание файлов для {sanitized_name}...")
    for filename, content in templates.items():
        file_path = service_path / filename
        file_path.write_text(content.strip() + "\n", encoding="utf-8")
    
    # Создание базового теста
    test_content = f'''"""Тесты для {sanitized_name}."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Проверка эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "{sanitized_name}"


def test_root():
    """Проверка корневой страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "{sanitized_name}"
    assert "version" in response.json()
'''
    (service_path / "tests" / "test_main.py").write_text(test_content, encoding="utf-8")
    
    return service_path


def update_docker_compose(service_name: str, base_path: Path) -> bool:
    """Добавить сервис в docker-compose.yml."""
    compose_path = base_path.parent / "docker-compose.yml"
    
    if not compose_path.exists():
        print("⚠️  docker-compose.yml не найден, пропуск")
        return False
    
    content = compose_path.read_text(encoding="utf-8")
    
    # Проверить, есть ли уже сервис
    if f"  {service_name}:" in content:
        print(f"⚠️  Сервис {service_name} уже есть в docker-compose.yml")
        return False
    
    # Добавить секцию сервиса
    service_config = f'''
  {service_name}:
    build:
      context: ./apps/{service_name}
      dockerfile: Dockerfile
    container_name: {service_name}
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
'''
    
    # Вставить перед last service или в конец
    content = content.rstrip() + service_config + "\n"
    compose_path.write_text(content, encoding="utf-8")
    
    print(f"✅ Добавлен {service_name} в docker-compose.yml")
    return True


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Генератор новых сервисов")
    parser.add_argument("name", type=str, help="Имя нового сервиса")
    parser.add_argument(
        "--description",
        type=str,
        default="Новый сервис",
        help="Описание сервиса"
    )
    parser.add_argument(
        "--add-compose",
        action="store_true",
        dest="add_compose",
        help="Добавить в docker-compose.yml"
    )
    
    args = parser.parse_args()
    
    # Найти базовый путь (предположим, что скрипт в scripts/)
    base_path = Path(__file__).parent.parent / "apps"
    
    print(f"\n{'=' * 80}")
    print(f"Создание нового сервиса: {args.name}")
    print(f"Описание: {args.description}")
    print(f"{'=' * 80}\n")
    
    # Создание сервиса
    service_path = create_service(args.name, args.description, base_path)
    
    if not service_path:
        sys.exit(1)
    
    print(f"\n✅ Сервис создан: {service_path}")
    
    # Добавить в docker-compose
    if args.add_compose:
        update_docker_compose(sanitize_name(args.name), base_path)
    
    # Вывод инструкций
    print(f"\n{'=' * 80}")
    print("Следующие шаги:")
    print(f"{'=' * 80}")
    print(f"1. cd apps/{sanitize_name(args.name)}")
    print(f"2. Отредактируйте main.py — добавьте бизнес-логику")
    print(f"3. Отредактируйте README.md — добавьте детали")
    print(f"4. python -m pytest — запустите тесты")
    print(f"5. docker-compose up {sanitize_name(args.name)} — запустите сервис")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
