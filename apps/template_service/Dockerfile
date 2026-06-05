# Template Service Dockerfile

FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app

# Копирование requirements
# Install git for pip dependencies from git+https://
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Экспортируемый порт
EXPOSE 8900

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8900"]
