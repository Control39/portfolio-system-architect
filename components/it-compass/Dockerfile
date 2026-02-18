# Использование официального образа Python
FROM python:3.13-slim

# Установка рабочей директории
WORKDIR /app

# Создание непривилегированного пользователя
# Группа с ID 1001, пользователь с ID 1001
RUN addgroup --gid 1001 --system appgroup && \
    adduser --uid 1001 --system --ingroup appgroup appuser

# Копирование requirements.txt для установки зависимостей
COPY requirements.txt .

# Установка зависимостей
# Обновление пакетов и установка curl для проверки зависимостей
RUN apt-get update && \
    apt-get install -y curl && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Копирование исходного кода приложения
COPY . .

# Установка прав доступа для директории приложения
# Пользователь appuser становится владельцем всех файлов
RUN chown -R appuser:appgroup /app && \
    find /app -type d -exec chmod 755 {} \; && \
    find /app -type f -exec chmod 644 {} \;

# Переключение на непривилегированного пользователя
USER appuser

# Установка переменной окружения для Python
# Отключение буферизации вывода и установка кодировки UTF-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# Проверка установки зависимостей
RUN python -c "import sys; print('Python version:', sys.version); print('Installed packages:'); [print(d) for d in __import__('pkg_resources').working_set]"

# Проверка доступности основного модуля
# Запуск скрипта для проверки импорта
RUN python -c "try: from src.main import main; print('Main module imported successfully') except ImportError as e: print(f'Import error: {e}'); exit(1)"

# Экспорт порта приложения
# Приложение будет доступно на порту 8000
EXPOSE 8000

# Создание директории для логов
# Директория будет доступна пользователю appuser
RUN mkdir -p /app/logs && \
    chown appuser:appgroup /app/logs

# Создание директории для временных файлов
# Директория будет доступна пользователю appuser
RUN mkdir -p /app/tmp && \
    chown appuser:appgroup /app/tmp

# Health check
# Периодическая проверка работоспособности приложения
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Аргументы сборки
# Позволяют передавать параметры при сборке образа
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Метаданные образа
# Информация о сборке, версии и источнике
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="it-compass" \
      org.label-schema.description="IT Architecture Compass" \
      org.label-schema.url="https://sourcecraft.dev/leadarchitect-ai/ekaterina-kudelya-it-compass" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://sourcecraft.dev/leadarchitect-ai/ekaterina-kudelya-it-compass.git" \
      org.label-schema.vendor="Lead Architect AI" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Точка входа в приложение
# Запуск основного приложения
CMD ["python", "src/main.py"]