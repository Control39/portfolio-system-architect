# Template Service

> **Статус:** 🟢 Production Ready
> **Версия:** 1.0.0
> **Владелец:** Portfolio System Architect Team

---

## 🎯 Назначение

Template Service — это шаблон для создания новых микросервисов в экосистеме Portfolio System Architect. Предоставляет готовую структуру проекта, базовую реализацию FastAPI приложения, конфигурацию и документацию для быстрого старта разработки.

### Ключевые возможности
- [x] Готовая структура проекта (src/, tests/, config/)
- [x] FastAPI приложение с health check
- [x] Интеграция с AI Config Manager
- [x] Dockerfile для контейнеризации
- [x] Базовая документация (README, CONTRIBUTING)
- [x] Примеры тестов и конфигураций

---

## 💼 Архитектурная ценность

### Для чего нужен Template Service

При создании нового микросервиса в экосистеме:
- **Стандартизация:** Все сервисы следуют единой структуре.
- **Скорость:** Не нужно настраивать проект с нуля.
- **Качество:** Включены лучшие практики (линтинг, тестирование, документация).
- **Интеграция:** Готовая интеграция с общими компонентами (AI Config Manager, логирование).

### Использование

```bash
# 1. Скопировать шаблон
cp -r apps/template-service apps/my-new-service

# 2. Переименовать внутренние ссылки
sed -i 's/template-service/my-new-service/g' apps/my-new-service/*

# 3. Настроить конфигурацию
# Редактировать config/service-config.yaml

# 4. Реализовать бизнес-логику в src/

# 5. Написать тесты в tests/

# 6. Запустить
cd apps/my-new-service
docker-compose up -d my-new-service
```

---

## 📁 Структура проекта

```
template-service/
├── src/                      # Исходный код
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── config_integration.py # Интеграция с AI Config Manager
│   └── ...
├── tests/                    # Тесты
│   ├── __init__.py
│   └── test_main.py
├── config/                   # Конфигурации
│   └── service-config.yaml
├── Dockerfile               # Контейнеризация
├── requirements.txt         # Зависимости
├── README.md                # Документация
└── ...
```

---

## 🚀 Быстрый старт

### Запуск через Docker

```bash
docker-compose up -d template-service
```

### Локальный запуск

```bash
cd apps/template-service
python -m uvicorn src.main:app --reload --port 8900
```

### Доступ к API

- **Swagger UI:** http://localhost:8900/docs
- **Redoc:** http://localhost:8900/redoc
- **Health check:** http://localhost:8900/health

---

## 📦 Зависимости

Основные зависимости (см. `requirements.txt`):

- **FastAPI** >= 0.100.0 — веб-фреймворк
- **Pydantic** >= 2.0.0 — валидация данных
- **Uvicorn** >= 0.20.0 — ASGI сервер
- **PyYAML** >= 6.0.0 — загрузка конфигов

Установка:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Разработка

### Запуск тестов

```bash
pytest --cov=src --cov-report=html
```

### Линтинг

```bash
ruff check .
black --check .
mypy src/
```

### Форматирование

```bash
black .
isort .
```

---

## 📝 Contributing

1. Fork репозиторий
2. Создайте ветку: `git checkout -b feature/your-feature`
3. Внесите изменения и протестируйте
4. Закоммитьте: `git commit -m "feat: описание"`
5. Push: `git push origin feature/your-feature`
6. Создайте Pull Request

**Правила:**
- Следуйте стилю Black + isort
- Добавьте тесты для новых функций
- Обновите документацию при необходимости

---

## 📊 Метрики

| Показатель | Значение |
|------------|----------|
| Тестов | **5** (100% проходят) |
| Покрытие | **~80%** (цель: 85%) |
| AI Config Manager | ✅ Integrated |
| Статус | 🟢 Production Ready |

---

## 🔗 Ссылки

- [Основной README](../../README.md)
- [Документация по архитектуре](../../docs/ARCHITECTURE.md)
- [Руководство по контрибуции](../../CONTRIBUTING.md)
- [AI Config Manager](../ai-config-manager/README.md)

---

**Автор:** Portfolio System Architect Team  
**Дата:** 18 мая 2026 г.
