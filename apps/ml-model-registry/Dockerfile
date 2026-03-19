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

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage - copy only wheels
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

# Copy built wheels
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY --chown=appuser:appuser . .
ENV PYTHONPATH=/app

USER appuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "src.core.registry:app", "--host", "0.0.0.0", "--port", "8001"]
