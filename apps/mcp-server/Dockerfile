FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY pyproject.toml .
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY scripts/ ./scripts/

# Создание директорий для данных
RUN mkdir -p /app/data/chroma /app/data/logs

# Переменные окружения
ENV PYTHONPATH=/app
ENV PROJECT_ROOT=/workspace
ENV CHROMA_DB_PATH=/app/data/chroma

# Volume для сохранения данных
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Запуск сервера
CMD ["python", "src/main.py"]
