# Dockerfile for Architect Assistant API (FastAPI + RAG)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../../pyproject.toml ../../README.md ./
COPY ../../src ./src
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directory for ChromaDB persistence
RUN mkdir -p /app/data/chroma_db /app/data/cache

# Environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIR=/app/data/chroma_db
ENV CACHE_DIR=/app/data/cache

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
