FROM python:3.12-slim

WORKDIR /app

# Сначала копируем всё (включая requirements-local.txt)
COPY . .
# Затем копируем корректный requirements.txt (переименовываем)
RUN cp requirements-local.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общие модули из корня проекта (контекст — apps/auth_service, поэтому ../src)
COPY ../src /app/shared_src

ENV PYTHONPATH=/app:/app/shared_src
ENV PATH="/root/.local/bin:${PATH}"

EXPOSE 8100

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
