# Portfolio Organizer

**Интеллектуальная система для организации и демонстрации компетенций**

Portfolio Organizer - это система, созданная архитектором когнитивных систем Екатериной Куделей. Этот проект демонстрирует, как можно автоматизировать процесс создания и представления портфолио, превращая хаос данных в структурированную, живую систему доказательств экспертизы.

## Описание

Portfolio Organizer предоставляет инструменты для структурирования, анализа и представления портфолио проектов, включая функции для веб-интерфейса, API и интеграции с различными источниками данных.

## Основные компоненты

### API
- **Reasoning API** - API для анализа и рекомендаций по проектам
- **ML Model Registry Integration** - Интеграция с реестром ML моделей

### Web Interface
- **HTML/CSS/JavaScript** - Веб-интерфейс для отображения портфолио

### Core Services
- **IT Compass API** - Интеграция с IT Compass для отслеживания компетенций
- **Notification Service** - Сервис уведомлений

### Integrations
- **IT-Compass** - Интеграция с системой отслеживания IT компетенций
- **Cloud-Reason** - Интеграция для автоматической генерации резюме и презентаций

## Установка

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите приложение:
   ```bash
   python src/app.py
   ```

## Использование

### Запуск веб-интерфейса

Приложение запускается на порту 5001 по умолчанию:

```bash
python src/app.py
```

### Использование API

```python
import requests

# Получение данных о портфолио
response = requests.get('http://localhost:5001/')
print(response.json())
```

## Демо и Бейджи

[![CI](https://github.com/Control39/portfolio-system-architect/actions/workflows/ci.yml/badge.svg)](https://github.com/Control39/portfolio-system-architect/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

**Демо проекта**: Запустите `docker compose up portfolio-organizer` для просмотра портфолио-органайзера на http://localhost:8004.

## История портфолио
Полная эволюция: [docs/PORTFOLIO-STORY.md](../docs/PORTFOLIO-STORY.md) | Матрица: [docs/PROJECTS-MATRIX.md](../docs/PROJECTS-MATRIX.md)

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для получения подробной информации.
