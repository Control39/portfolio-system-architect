# Portfolio Organizer

Portfolio Organizer - это система, созданная архитектором когнитивных систем Екатериной Куделей. Этот проект демонстрирует, как можно автоматизировать процесс создания и представления портфолио, превращая хаос данных в структурированную, живую систему доказательств экспертизы.

## Описание

Portfolio Organizer предоставляет инструменты для структурирования, анализа и представления портфолио проектов, включая функции для веб-интерфейса, API и интеграции с различными источниками данных.

## Основные компоненты

### API
- **Reasoning API** - API для анализа и рекомендаций по проектам
- **Mobile API** - API для мобильных приложений
- **Demo API** - Демонстрационный API

### Web Interface
- **HTML/CSS** - Веб-интерфейс для отображения портфолио

### Analytics
- **Advanced Analytics** - Расширенные аналитические функции

### Integrations
- **Market Data** - Интеграция с рыночными данными

### Notifications
- **Notification Service** - Сервис уведомлений

## Установка

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите веб-интерфейс:
   ```bash
   python src/web/app.py
   ```

## Использование

### Запуск веб-интерфейса

```bash
python src/web/app.py
```

### Использование API

```python
import requests

# Получение данных о портфолио
response = requests.get('http://localhost:5000/api/portfolio')
print(response.json())
```

## Демо и Бейджи

[![CI](https://github.com/Control39/cognitive-systems-architecture/actions/workflows/ci.yml/badge.svg)](https://github.com/Control39/cognitive-systems-architecture/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)
[![Live Demo](http://localhost:8004)](http://localhost:8004)

**Демо проекта**: Запустите `docker compose up portfolio-organizer` для просмотра портфолио-органайзера на http://localhost:8004.

## История портфолио
Полная эволюция: [docs/PORTFOLIO-STORY.md](../docs/PORTFOLIO-STORY.md) | Матрица: [docs/PROJECTS-MATRIX.md](../docs/PROJECTS-MATRIX.md)

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для получения подробной информации.



