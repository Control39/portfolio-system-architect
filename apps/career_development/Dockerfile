FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Копируем общие модули из корня проекта (контекст — apps/career_development, поэтому ../src)
COPY ../src /app/shared_src

ENV PYTHONPATH=/app:/app/shared_src
ENV PATH="/root/.local/bin:${PATH}"

EXPOSE 8200

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]
