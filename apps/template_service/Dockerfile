# Template Service Dockerfile

FROM python:3.11-slim

# Установка зависимостей
WORKDIR /app

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Экспортируемый порт
EXPOSE 8900

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8900"]