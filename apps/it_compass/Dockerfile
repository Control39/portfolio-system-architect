FROM python:3.11-slim

LABEL maintainer="Ekaterina Kudelya"
LABEL description="IT Compass - Objective IT Career Growth Tracker"
LABEL version="1.0.0"
LABEL methodology="© 2025 Ekaterina Kudelya, CC BY-ND 4.0"

WORKDIR /app

# Копируем requirements из КОРНЯ (общие зависимости)
COPY requirements.txt /tmp/requirements-root.txt
RUN if [ -f /tmp/requirements-root.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-root.txt; \
    fi

# Копируем requirements из сервиса (специфичные зависимости)
COPY apps/it_compass/requirements.txt /tmp/requirements-service.txt
RUN if [ -f /tmp/requirements-service.txt ]; then \
    pip install --no-cache-dir -r /tmp/requirements-service.txt; \
    fi

# Копируем src/ (общие компоненты)
COPY src/ /app/src

# Копируем папку сервиса
COPY apps/it_compass/ /app

# Конфигурация
ENV PYTHONPATH=/app:/app/src
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_LOGGER_LEVEL=error
ENV STREAMLIT_CLIENT_GATHER_USAGE_STATS=false

# Удаляем временные requirements
RUN rm -f /tmp/requirements-*.txt

# Streamlit конфигурация (до создания пользователя)
RUN mkdir -p /app/.streamlit && \
    echo '[logger]\nlevel = "error"\n\n[client]\ngatherUsageStats = false' > /app/.streamlit/config.toml

# Создание непривилегированного пользователя с home dir
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --home-dir /home/appuser -m appuser

# Установка прав доступа
RUN chown -R appuser:appgroup /app /home/appuser

# Установка пользователя по умолчанию
USER appuser

# Streamlit запуск (NOT FastAPI)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
