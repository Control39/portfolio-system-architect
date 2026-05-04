# 🚀 Deployment Guide

**Last Updated**: 2026-05-04  
**Version**: 2.0 (Production Ready)  
**Status**: 🟢 Fully Documented

---

## 📚 Quick Navigation

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Environment Setup](#environment-setup)
5. [Health Checks](#health-checks)
6. [Troubleshooting](#troubleshooting)

---

## 💻 Local Development

### Prerequisites
```bash
# Python 3.10+
python --version

# Git
git --version

# Docker (optional)
docker --version
```

### Setup

```bash
# Clone repository
git clone https://github.com/Control39/portfolio-system-architect.git
cd portfolio-system-architect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install services
pip install -e apps/cognitive-agent
pip install -e apps/decision-engine
# ... install other services
```

### Run Locally

```bash
# Single service
cd apps/cognitive-agent
python -m uvicorn src.main:app --reload --port 8000

# All services (docker-compose)
docker-compose -f docker-compose.dev.yml up

# Run tests
python -m pytest apps/*/tests/test_basic.py -v
```

### Health Check

```bash
# Service health
python health_check.py

# Individual service
curl http://localhost:8000/health
```

---

## 🐳 Docker Deployment

### Build

#### Single Service
```bash
cd apps/cognitive-agent

# Build image
docker build -f ../../docker/cognitive-agent/Dockerfile \
  -t portfolio-architect/cognitive-agent:latest \
  ../..

# Tag for registry
docker tag portfolio-architect/cognitive-agent:latest \
  registry.example.com/portfolio-architect/cognitive-agent:latest
```

#### All Services
```bash
# Build all
docker-compose build

# Tag all
for service in cognitive-agent decision-engine it_compass knowledge-graph \
               auth_service mcp-server infra-orchestrator ml-model-registry \
               portfolio_organizer career_development job-automation-agent \
               ai-config-manager template-service system-proof thought-architecture; do
  docker tag portfolio-architect/$service:latest \
    registry.example.com/portfolio-architect/$service:latest
done
```

### Run Locally with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  cognitive-agent:
    build: ./apps/cognitive-agent
    ports:
      - "8001:8000"
    environment:
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=dev-password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Push to Registry

```bash
# Docker Hub
docker push registry.example.com/portfolio-architect/cognitive-agent:latest

# Private registry
docker tag portfolio-architect/cognitive-agent:latest \
  your-registry.azurecr.io/cognitive-agent:latest
az acr login --name your-registry
docker push your-registry.azurecr.io/cognitive-agent:latest
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
kubectl version --client

# Configure kubeconfig
export KUBECONFIG=~/.kube/config

# Verify cluster access
kubectl cluster-info
```

### Namespace Setup

```bash
# Create namespace
kubectl create namespace portfolio

# Set default namespace
kubectl config set-context --current --namespace=portfolio
```

### Deploy Services

#### 1. Secrets

```bash
# Create secrets
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secure-password

kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password
```

#### 2. ConfigMap

```bash
# Create configuration
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=INFO \
  --from-literal=API_TIMEOUT=30 \
  --from-file=config/
```

#### 3. Deploy Service

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cognitive-agent
  namespace: portfolio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cognitive-agent
  template:
    metadata:
      labels:
        app: cognitive-agent
    spec:
      containers:
      - name: cognitive-agent
        image: registry.example.com/portfolio-architect/cognitive-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
      imagePullSecrets:
      - name: regcred
```

```bash
# Deploy
kubectl apply -f deployment.yaml

# Verify
kubectl get deployments
kubectl get pods
kubectl describe deployment cognitive-agent
```

#### 4. Expose Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cognitive-agent
  namespace: portfolio
spec:
  selector:
    app: cognitive-agent
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

```bash
# Apply
kubectl apply -f service.yaml

# Test
kubectl port-forward svc/cognitive-agent 8000:80
curl http://localhost:8000/health
```

#### 5. Ingress Setup

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portfolio-ingress
  namespace: portfolio
spec:
  rules:
  - host: api.portfolio.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cognitive-agent
            port:
              number: 80
  - host: decision.portfolio.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: decision-engine
            port:
              number: 80
```

```bash
# Deploy ingress
kubectl apply -f ingress.yaml
```

### Deploy All Services

```bash
# Apply all manifests in order
kubectl apply -f k8s/namespaces.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress.yaml

# Or use Kustomize
kubectl apply -k k8s/overlays/production/
```

### Verify Deployment

```bash
# Check all pods
kubectl get pods --all-namespaces

# Check services
kubectl get services -n portfolio

# Check ingress
kubectl get ingress -n portfolio

# View logs
kubectl logs -f deployment/cognitive-agent -n portfolio

# Check events
kubectl get events -n portfolio --sort-by='.lastTimestamp'
```

---

## ⚙️ Environment Setup

### Development

```bash
# .env.dev
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://dev:dev@localhost:5432/portfolio_dev
REDIS_URL=redis://localhost:6379
API_TIMEOUT=30
DEBUG=true
```

### Staging

```bash
# .env.staging
LOG_LEVEL=INFO
DATABASE_URL=postgresql://staging:password@staging-db.example.com:5432/portfolio
REDIS_URL=redis://staging-redis.example.com:6379
API_TIMEOUT=10
DEBUG=false
SENTRY_DSN=https://key@sentry.example.com/1234
```

### Production

```bash
# .env.prod (secure storage)
LOG_LEVEL=WARN
DATABASE_URL=postgresql://prod:${SECURE_PASSWORD}@prod-db.example.com:5432/portfolio
REDIS_URL=redis://prod-redis.example.com:6379
API_TIMEOUT=5
DEBUG=false
SENTRY_DSN=https://key@sentry.example.com/5678
ENABLE_METRICS=true
ENABLE_TRACING=true
```

### Database Initialization

```bash
# Run migrations
python -m alembic upgrade head

# Seed initial data
python scripts/seed_data.py

# Verify
python -c "from src.db import get_session; \
           session = get_session(); \
           count = session.query(User).count(); \
           print(f'Users: {count}')"
```

---

## 🏥 Health Checks

### Endpoint Health

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed

# Dependencies health
curl http://localhost:8000/health/dependencies
```

### Response Format

```json
{
  "status": "healthy",
  "timestamp": "2026-05-04T12:00:00Z",
  "version": "2.0.0",
  "uptime": 3600,
  "dependencies": {
    "database": {
      "status": "healthy",
      "latency": "10ms"
    },
    "redis": {
      "status": "healthy",
      "latency": "5ms"
    },
    "mcp-server": {
      "status": "healthy",
      "latency": "50ms"
    }
  }
}
```

### Kubernetes Health Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 2
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs <container-id>
kubectl logs deployment/<service-name>

# Check configuration
cat /app/config/default.yaml

# Check dependencies
curl http://postgres:5432  # Should fail but connect
redis-cli -h redis ping    # Should respond PONG
```

### High Latency

```bash
# Check service metrics
kubectl top pods

# Check database
kubectl exec -it postgres-pod -- psql -U postgres -d portfolio \
  -c "SELECT COUNT(*) FROM pg_stat_statements WHERE mean_time > 1000;"

# Check Redis
redis-cli --stat

# Check network
kubectl top nodes
kubectl describe node <node-name>
```

### Connection Issues

```bash
# Test network connectivity
kubectl exec <pod> -- curl http://cognitive-agent:8000/health

# Check DNS
kubectl exec <pod> -- nslookup cognitive-agent

# Check service discovery
kubectl get endpoints cognitive-agent

# Test load balancing
for i in {1..5}; do \
  kubectl exec <pod> -- curl -s http://cognitive-agent:8000/hostname; \
done
```

### Database Issues

```bash
# Check connection pool
kubectl exec <pod> -- \
  python -c "from src.db import engine; \
             print(engine.pool.size(), engine.pool.checked_in())"

# Check migrations
python -m alembic current
python -m alembic history

# Reset database (dev only!)
python -m alembic downgrade base
python -m alembic upgrade head
python scripts/seed_data.py
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

```bash
# Access metrics
curl http://localhost:9090/api/v1/query?query=up

# Service availability
curl http://localhost:9090/api/v1/query?query=service:available

# Error rate
curl http://localhost:9090/api/v1/query?query=service:error_rate
```

### Grafana Dashboards

```bash
# Access Grafana
open http://localhost:3000

# Default credentials
username: admin
password: admin

# Import dashboards
- Service Health
- Database Performance
- API Latency
- Resource Utilization
```

### Logging

```bash
# Elasticsearch
curl http://elasticsearch:9200/_search?q=level:ERROR

# View logs
kibana  # http://localhost:5601

# Log levels
- DEBUG: Detailed information
- INFO: General information
- WARN: Warning messages
- ERROR: Error messages
```

---

## 🔐 Security

### TLS/HTTPS

```yaml
# Ingress with TLS
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: portfolio-ingress
spec:
  tls:
  - hosts:
    - api.portfolio.example.com
    secretName: portfolio-tls
  rules:
  - host: api.portfolio.example.com
    http:
      paths:
      - path: /
        backend:
          service:
            name: cognitive-agent
            port:
              number: 80
```

### Secrets Rotation

```bash
# Rotate database password
kubectl patch secret db-credentials \
  -p '{"data":{"password":"'$(echo -n newpass | base64)'"}}'

# Rotate certificates
cert-manager renew portfolio-tls --namespace portfolio
```

### Network Policies

```yaml
# Allow only from ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ingress-controller
```

---

## 🚚 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build and push Docker image
      run: |
        docker build -t registry/cognitive-agent:${{ github.sha }} .
        docker push registry/cognitive-agent:${{ github.sha }}
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/cognitive-agent \
          cognitive-agent=registry/cognitive-agent:${{ github.sha }}
```

---

## 📋 Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Docker image builds successfully
- [ ] Configuration files ready
- [ ] Database migrations prepared
- [ ] Secrets configured
- [ ] Ingress DNS updated

### Post-Deployment
- [ ] All pods running
- [ ] Health checks passing
- [ ] Metrics visible in Prometheus
- [ ] Logs in Elasticsearch
- [ ] Smoke tests passed
- [ ] Rollback plan prepared

---

**Status**: 🟢 Production Ready  
**Last Updated**: 2026-05-04

