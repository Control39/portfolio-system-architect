FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
COPY cloud_reason /app/cloud_reason
COPY component-config.yaml /app/component-config.yaml
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

CMD ["uvicorn", "cloud_reason.main:app", "--host", "0.0.0.0", "--port", "8000"]
