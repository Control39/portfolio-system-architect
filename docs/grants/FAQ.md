# FAQ for Grant Defense

| Вопрос | Ответ |
|--------|-------|
| Какой статус проекта? | Stage 2 Enterprise ✅: K8s, Terraform, monitoring, DR |
| Dependencies? | [project-config.yaml](project-config.yaml), requirements-dev.txt |
| Tests coverage? | 90%+ [pytest.ini](pytest.ini), tests/e2e/, tests/unit/ |
| Deployment? | K8s manifests [deployment/k8s/](deployment/k8s/), docker-compose.yml |
| Security? | .pre-commit-config.yaml (bandit, secrets), sealed-secrets |
| Architecture? | [ARCHITECTURE.md](docs/ARCHITECTURE.md), 8 microservices |
| Innovation? | GigaChain MCP bridge [src/cloud_reason/gigachain_bridge.py](src/cloud_reason/gigachain_bridge.py) |
| Terraform? | [packages/terraform/](packages/terraform/) |
| Monitoring? | Prometheus/Grafana [monitoring/](monitoring/) |
| DR? | [DR_RUNBOOK.md](DR_RUNBOOK.md), postgres backups |
| Next steps? | Stage 3: Production AI Agents, Yandex Cloud integration |

