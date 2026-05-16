# 🐳 Docker Конфигурации

> **Подробное описание:** См. [`../../.reports/docker-report.md`](../../.reports/docker-report.md)

## 🚀 Быстрый старт

```bash
# Запуск всего стека
docker-compose up -d

# Запуск с мониторингом
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Остановка
docker-compose down
```

## 📁 Структура

- `base-images/` — базовые образы (Python, UI)
- `postgres-init/` — скрипты инициализации БД
- `docker-compose.*.yml` — модульные конфигурации (мониторинг, MLflow, RAG, gateway)

## 🔗 Ссылки

- [Полный отчёт](../../.reports/docker-report.md)
- [Makefile](../../Makefile) — команды `make docker-up`, `make docker-down`
- [docker-compose.yml](../docker-compose.yml) — основной файл
