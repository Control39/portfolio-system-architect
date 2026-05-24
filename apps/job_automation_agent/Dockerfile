FROM python:3.11-slim

WORKDIR /app

# Копируем requirements из КОРНЯ (общие зависимости)
COPY requirements.txt /tmp/requirements-root.txt
RUN if [ -f /tmp/requirements-root.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-root.txt; \
    fi

# Копируем requirements из сервиса (специфичные зависимости)
COPY apps/job_automation_agent/requirements.txt /tmp/requirements-service.txt
RUN if [ -f /tmp/requirements-service.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-service.txt; \
    fi

# Копируем src/ (общие компоненты)
COPY src/ /app/src

# Копируем папку сервиса
COPY apps/job_automation_agent/ /app

# Конфигурация
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Удаляем временные requirements
RUN rm -f /tmp/requirements-*.txt

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
