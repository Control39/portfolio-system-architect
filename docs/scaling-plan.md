# План Масштабирования Portfolio System Architect

## Текущий статус
- Docker Compose: 7 services, Grafana monitoring
- CI: pytest/cov GitHub Actions

## Горизонтальное масштабирование (Q2 2026)
1. **Kubernetes manifests**: Deploy to k8s (minikube local)
   - HorizontalPodAutoscaler CPU>70%
   - Services LoadBalancer
2. **Queues**: Celery + Redis for async (it-compass markers)
3. **DB**: Postgres HA (replicas)

## Вертикальное (immediate)
- ml-model-registry memory 4G → 8G
- Cache: Redis for RAG queries (cloud-reason)

## Roadmap
| Phase | Action | Timeline |
|-------|--------|----------|
| MVP | Docker + CI | Done |
| Scale1 | Redis + Celery | 1 week |
| Prod | K8s + Postgres HA | 1 month |

Tags: #scaling #roadmap

