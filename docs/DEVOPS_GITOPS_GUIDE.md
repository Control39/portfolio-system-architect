# GitOps Guide for Portfolio System

## Overview

This guide describes the GitOps workflow implemented for the Portfolio System. GitOps is a methodology where the entire system state is declared in Git, and automated processes ensure the live environment matches the declared state.

## Architecture

- **Git Repository**: Single source of truth for all Kubernetes manifests, Helm charts, and deployment configurations.
- **CI/CD Pipeline**: GitHub Actions for building, testing, and security scanning.
- **GitOps Operator**: Argo CD (or manual `kubectl apply -k`) synchronizes the Kubernetes cluster with the Git repository.
- **Environments**: Staging (auto‑deploy on `main`), Production (manual approval).

## Directory Structure

```
deployment/
├── gitops/
│   ├── README.md                 # GitOps overview
│   ├── deploy.sh                 # Bootstrap script
│   └── argo-app.yaml             # Argo CD Application definitions
├── k8s/
│   ├── base/                     # Common Kustomize bases
│   │   └── services/             # Per‑service definitions
│   └── overlays/
│       ├── dev/                  # Development overlays
│       ├── staging/              # Staging overlays (auto‑deployed)
│       └── prod/                 # Production overlays
└── secrets/                      *Encrypted secrets (SOPS / Sealed Secrets)
```

## Workflow

### 1. Development

- Developers work on feature branches.
- Changes to application code, Dockerfiles, or Kubernetes manifests are committed and pushed.
- Pull requests trigger CI (security, lint, test, build).

### 2. Continuous Integration

The CI pipeline (`/.github/workflows/ci.yml`) runs:

- **Security checks** (detect‑secrets, safety, pip‑audit, Trivy, license compliance)
- **Linting & formatting** (pre‑commit, Ruff, Black)
- **Unit & integration tests** with PostgreSQL service
- **Docker image build** (multi‑arch) and push to GHCR (only on `main`)

### 3. Continuous Deployment (GitOps)

When a commit lands on `main`:

1. CI builds and pushes the new Docker images.
2. The `deploy‑gitops` job applies the staging overlay via `kubectl apply -k`.
3. Argo CD (if installed) detects the Git change and automatically syncs the cluster.

### Manual Deployment

For production or emergency rollbacks, use the bootstrap script:

```bash
cd deployment/gitops
./deploy.sh --env staging
```

## Argo CD Setup

If you have Argo CD installed in your cluster, apply the Application manifests:

```bash
kubectl apply -f deployment/gitops/argo-app.yaml
```

This creates two Argo CD Applications:

- `portfolio-system` – deploys the main services (IT Compass, Cloud Reason, ML Model Registry, Portfolio Organizer) to the `portfolio` namespace.
- `portfolio-monitoring` – deploys Prometheus, Grafana, Alertmanager to the `monitoring` namespace.

## Secrets Management

Secrets are managed with **Kubernetes Sealed Secrets** (or **SOPS**). Encrypted secret files are stored in `deployment/secrets/`. The CI pipeline does **not** have decryption keys; secrets are decrypted only inside the cluster.

To create a new sealed secret:

```bash
# Install kubeseal
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml
```

## Rollback

Because every change is versioned in Git, rolling back is a matter of reverting the commit and letting GitOps sync. Alternatively, you can manually apply a previous revision:

```bash
git checkout <old-commit> -- deployment/k8s/overlays/staging
kubectl apply -k deployment/k8s/overlays/staging
```

## Monitoring & Observability

- **Prometheus** scrapes metrics from all services.
- **Grafana** dashboards show application performance, error rates, and business metrics.
- **Alertmanager** sends notifications to Slack/Telegram when thresholds are breached.

## Troubleshooting

### Argo CD out of sync

Check the Argo CD UI or run:

```bash
kubectl get application -n argocd
kubectl describe application portfolio-system -n argocd
```

### Deployment stuck

Inspect the rollout status:

```bash
kubectl rollout status deployment/it-compass -n portfolio
kubectl describe deployment/it-compass -n portfolio
kubectl logs deployment/it-compass -n portfolio
```

### Image pull errors

Ensure the image tag exists in the container registry and the pull secret is configured.

## Next Steps

- Implement **canary deployments** using Flagger.
- Add **cost‑monitoring** with OpenCost.
- Set up **backup & disaster recovery** with Velero.

## References

- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [Kustomize](https://kubectl.docs.kubernetes.io/guides/introduction/kustomize/)
- [GitOps Principles](https://www.gitops.tech/)