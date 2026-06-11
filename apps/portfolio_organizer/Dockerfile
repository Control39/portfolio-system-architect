# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install curl and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git && rm -rf /var/lib/apt/lists/*

# Копируем requirements из КОРНЯ (общие зависимости)
COPY requirements.txt /tmp/requirements-root.txt
RUN if [ -f /tmp/requirements-root.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-root.txt; \
    fi

# Копируем requirements из сервиса (специфичные зависимости)
COPY apps/portfolio_organizer/requirements.txt /tmp/requirements-service.txt
RUN if [ -f /tmp/requirements-service.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-service.txt; \
    fi

# Копируем src/ (общие компоненты)
COPY src/ /app/src

# ✅ ИСПРАВЛЕНИЕ: Копируем ВСЁ из apps/ в /app (включая portfolio_organizer, auth_service и т.д.)
COPY apps/ /app/apps/

# Конфигурация
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1

# Удаляем временные requirements
RUN rm -f /tmp/requirements-*.txt

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8004

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# ✅ Запуск из /app/apps/portfolio_organizer/run_api.py
CMD ["python", "/app/apps/portfolio_organizer/run_api.py", "--mode", "dev"]
