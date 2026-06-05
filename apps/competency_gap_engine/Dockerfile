### 🐳 4. `apps/competency_gap_engine/Dockerfile`
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
# Install git for pip dependencies from git+https://
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY apps/competency_gap_engine/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Копируем зависимости и код
COPY --from=builder /install /usr/local
COPY apps/competency_gap_engine/ ./
COPY src/ ./src/

# Безопасность: non-root пользователь
RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONPATH=/app:/app/src \
    LOG_LEVEL=info \
    PORT=8300

EXPOSE 8300

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8300/health')"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8300", "--log-level", "info"]
