FROM python:3.12-slim

WORKDIR /app

# Копируем requirements из КОРНЯ (общие зависимости)
COPY requirements.txt /tmp/requirements-root.txt
RUN if [ -f /tmp/requirements-root.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-root.txt; \
    fi

# Копируем requirements из сервиса (специфичные зависимости)
COPY apps/auth_service/requirements.txt /tmp/requirements-service.txt
RUN if [ -f /tmp/requirements-service.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-service.txt; \
    fi

# Копируем src/ (общие компоненты для всех сервисов)
COPY src/ /app/src

# Копируем папку auth_service
COPY apps/auth_service/ /app

# Конфигурация
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:${PATH}"

# Удаляем временные requirements после установки
RUN rm -f /tmp/requirements-*.txt

EXPOSE 8100

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
