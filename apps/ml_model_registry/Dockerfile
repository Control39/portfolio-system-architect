FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies for compiled wheels (numpy, scikit, mlflow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from service directory (relative to build context)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Runtime deps only + curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libblas3 \
    liblapack3 \
    libopenblas0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Copy built packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy shared src from project root
COPY --chown=appuser:appuser src /app/src

# Copy service code
COPY . .

ENV PYTHONPATH=/app

USER appuser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
