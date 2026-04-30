FROM python:3.11-slim

LABEL maintainer="Ekaterina Kudelya"
LABEL description="IT Compass - Objective IT Career Growth Tracker"
LABEL version="1.0.0"
LABEL methodology="© 2025 Ekaterina Kudelya, CC BY-ND 4.0"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY setup.sh ./
RUN chmod +x setup.sh

# Создание непривилегированного пользователя
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Установка прав доступа для файлов приложения
RUN chown -R appuser:appgroup /app

# Установка пользователя по умолчанию
USER appuser

CMD ["python", "src/main.py"]
