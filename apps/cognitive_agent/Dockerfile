FROM python:3.12-slim

WORKDIR /app

# Install git for pip dependencies from git repos
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
# Install git for pip dependencies from git+https://
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements-root.txt
RUN if [ -f /tmp/requirements-root.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-root.txt; \
    fi

# Копируем requirements из сервиса (специфичные зависимости)
COPY apps/cognitive_agent/requirements.txt /tmp/requirements-service.txt
RUN if [ -f /tmp/requirements-service.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-service.txt; \
    fi

# Копируем src/ (общие компоненты)
COPY src/ /app/src

# Копируем папку сервиса
COPY apps/cognitive_agent/ /app

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
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
