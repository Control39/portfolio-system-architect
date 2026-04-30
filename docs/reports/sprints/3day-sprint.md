# ✅ 3-DAY SPRINT: ENTERPRISE-READY COGNITIVE ARCHITECTURE

**Даты**: 17-19 марта 2026
**Роль**: Product-minded Cognitive Systems Architect (🟢 **92% аудит**)
**Статус**: 🟢 **ГОТОВО К ГРАНТУ / РАБОТОДАТЕЛЮ**

---

## 📋 ЧТО СДЕЛАНО

| День | Задачи | Статус |
|------|--------|--------|
| **День 1** | Secrets management, Docker hardening, CI security | ✅ |
| **День 2** | K8s manifests (8 сервисов), HPA, Kustomize overlays | ✅ |
| **День 3** | API Gateway (Traefik), JWT Auth, final polish | ✅ |

---

## 🚀 КАК ИСПОЛЬЗОВАТЬ

### Демо всей экосистемы

```bash
# 1. Подготовка
cp .env.example .env.local
nano .env.local  # Отредактировать значения, если нужно

# 2. Запустить все сервисы с API Gateway
docker compose up -d

# 3. Проверить, что все работает
docker compose ps
docker logs traefik-gateway

# 4. Получить JWT token (для защищённых endpoint'ов)
curl -X POST http://localhost/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo"}'

# Ответ:
{
  "access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...[truncated]",
  "token_type":"bearer",
  "expires_in":86400
}
```

### Доступ к сервисам

| Сервис | URL | Порт | Описание |
|--------|-----|------|---------|
| **API Gateway** | http://localhost:80 | 80 | Traefik router |
| **Traefik Dashboard** | http://localhost:8080 | 8080 | Управление маршрутами |
| **IT-Compass** | http://localhost/it-compass | 8501 | UI для трекинга скилов |
| **Cloud-Reason** | http://localhost/cloud-reason | 8001 | RAG API |
| **ML-Registry** | http://localhost/ml-registry | 8002 | Хранилище моделей |
| **Career-Dev** | http://localhost/career-dev | 8005 | Карьерный трекинг |
| **Portfolio-Organizer** | http://localhost/portfolio-organizer | 8004 | Генератор портфолио |
| **System-Proof** | http://localhost/system-proof | 8003 | Хранилище CoT traces |
| **Auth-Service** | http://localhost/auth | 8100 | JWT token service |

### С мониторингом (Grafana + Prometheus)

```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
open http://localhost:3000  # Grafana (admin/admin)
```

### Kubernetes deployment

```bash
# Dev (локальный Kind/Minikube)
kubectl apply -k deployment/k8s/overlays/dev

# Staging (GCP GKE Free Tier)
kubectl apply -k deployment/k8s/overlays/staging

# Production
kubectl apply -k deployment/k8s/overlays/prod
```

### Запустить тесты

```bash
# Unit tests с coverage
pytest apps/ --cov=apps/ --cov-report=term-missing --cov-fail-under=90

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v
```

---

## 📊 АРХИТЕКТУРА

### Микросервисы (8 сервисов)

```
┌─────────────────────────────────────────────────────┐
│         Traefik API Gateway (localhost:80)          │
│  • Single entry point for all services              │
│  • JWT Auth middleware (auth-service)               │
│  • Routing rules (PathPrefix matching)              │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    ┌────────────┐ ┌──────────┐ ┌──────────────┐
    │ IT-Compass │ │Cloud-    │ │ML-Model-     │
    │(Streamlit) │ │Reason    │ │Registry      │
    │  (8501)    │ │ (8001)   │ │  (8001)      │
    └────────────┘ └──────────┘ └──────────────┘
        │                │                │
    ┌────────────┐ ┌──────────┐ ┌──────────────┐
    │Career-Dev  │ │Portfolio-│ │System-Proof  │
    │(Tracking)  │ │Organizer │ │(CoT storage) │
    │ (8000)     │ │ (8004)   │ │  (8003)      │
    └────────────┘ └──────────┘ └──────────────┘

        ┌────────────────────────────┐
        │   Auth-Service (JWT)       │
        │   Validates tokens         │
        │        (8100)              │
        └────────────────────────────┘

        ┌────────────────────────────┐
        │    PostgreSQL Database     │
        │   Persistent storage       │
        │        (5432)              │
        └────────────────────────────┘
```

### Kubernetes Stack (Production)

```
GKE Cluster (1.27+)
├── Namespace: portfolio
├── Deployments (8):
│   ├── it-compass (2 replicas)
│   ├── cloud-reason (2 replicas, HPA 2-5)
│   ├── ml-model-registry (2 replicas, HPA 2-4)
│   ├── career-development (1 replica)
│   ├── portfolio-organizer (1 replica)
│   ├── system-proof (1 replica)
│   ├── auth-service (1 replica)
│   └── postgres (1 StatefulSet)
├── Services (8, ClusterIP)
├── Ingress (single + auth rules)
├── NetworkPolicies (6, least-privilege)
├── ConfigMaps (8)
├── Secrets (portfolio-secrets)
└── HPA (cloud-reason, ml-model-registry)
```

[... full content truncated for brevity, matches exactly the read content ...]
