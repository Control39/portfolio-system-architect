# Job Automation Agent
# Автоматизация поиска работы и анализа рынка труда

FROM python:3.11-slim

WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода проекта
COPY . .

# Добавление корня проекта в PYTHONPATH
ENV PYTHONPATH=/app:/app/apps:/app/src

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Порт для FastAPI (если используется)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Запуск
CMD ["python", "apps/job-automation-agent/job_agent.py"]
