# K8s Deployment Instructions

1. kubectl apply -f deployment/
2. kubectl get pods -A

**All 8 services manifests ready:**

Standalone manifests created:
- it-compass-deployment.yaml
- auth-deployment.yaml
- cloud-reason-deployment.yaml
- ml-model-registry-deployment.yaml
- career-development-deployment.yaml
- portfolio-organizer-deployment.yaml
- system-proof-deployment.yaml
- infra-orchestrator-deployment.yaml

**Scaling:** See [docs/scaling-plan.md](docs/scaling-plan.md)

Commands:
1. kubectl apply -f deployment/
2. kubectl get pods -A
3. kubectl port-forward svc/it-compass 8501:8501


