# Базовый образ для Python микросервисов
# Используется всеми Python сервисами в проекте для обеспечения единообразия и оптимизации

ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} AS builder

# Метаданные образа
LABEL maintainer="portfolio-system-architect"
LABEL description="Базовый образ Python для микросервисов"
LABEL version="1.0.0"

WORKDIR /app

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка базовых Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    pydantic-settings==2.1.0 \
    sqlalchemy==2.0.23 \
    asyncpg==0.29.0 \
    python-dotenv==1.0.0 \
    httpx==0.25.1 \
    structlog==23.2.0 \
    prometheus-client==0.19.0

# Финальный образ (минимальный)
FROM python:${PYTHON_VERSION}

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Настройка пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Рабочая директория для приложения
WORKDIR /app

# Команда по умолчанию (переопределяется в дочерних образах)
CMD ["python", "-c", "print('Базовый образ Python готов к использованию')"]
