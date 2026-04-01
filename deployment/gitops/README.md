# GitOps Automation for Portfolio System Architect

This directory contains GitOps configuration for automated deployment using Argo CD or Flux.

## Overview

GitOps principles:
- **Declarative**: All Kubernetes manifests stored in Git.
- **Automated**: Changes to manifests trigger automatic deployment.
- **Observable**: Health and sync status visible via UI.

## Options

### 1. Argo CD (Recommended)

Argo CD is a Kubernetes-native continuous delivery tool.

#### Installation (Local)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Configure Application

Create `portfolio-app.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: portfolio-system
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/leadarchitect-ai/portfolio-system-architect.git
    targetRevision: main
    path: deployment/k8s/overlays/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: portfolio
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

Apply:

```bash
kubectl apply -f portfolio-app.yaml
```

### 2. Flux CD

Flux is another popular GitOps operator.

#### Installation

```bash
flux bootstrap github \
  --owner=leadarchitect-ai \
  --repository=portfolio-system-architect \
  --branch=main \
  --path=deployment/k8s/overlays/staging \
  --personal
```

### 3. Simple GitOps Script

If you don't want to install an operator, you can use a simple script that runs `kubectl apply -k` on a schedule (e.g., via GitHub Actions).

Script: `deploy.sh`

```bash
#!/bin/bash
set -e

echo "Deploying Portfolio System..."
kubectl apply -k deployment/k8s/overlays/staging
kubectl rollout status deployment/it-compass -n portfolio --timeout=300s
kubectl rollout status deployment/cloud-reason -n portfolio --timeout=300s
kubectl rollout status deployment/ml-model-registry -n portfolio --timeout=300s
echo "Deployment completed."
```

## Integration with CI/CD

The existing GitHub Actions workflow (`ci.yml`) already builds and pushes images. You can extend it with a deployment step that uses the GitOps approach.

Example step:

```yaml
- name: Deploy to Kubernetes (GitOps)
  if: github.ref == 'refs/heads/main'
  run: |
    kubectl apply -k deployment/k8s/overlays/staging
```

## Health Checks

After deployment, verify with:

```bash
kubectl get applications -n argocd
kubectl get pods -n portfolio
kubectl get svc -n portfolio
```

## Rollback

With GitOps, rollback is as simple as reverting the Git commit. Argo CD will automatically sync to the previous state.

```bash
git revert HEAD
git push origin main
```

## Security Considerations

- Use sealed secrets for sensitive data.
- Limit access to the Git repository.
- Enable branch protection on main.
- Use RBAC in Kubernetes to restrict Argo CD's permissions.

## References

- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [Flux Documentation](https://fluxcd.io/docs/)
- [GitOps Principles](https://www.gitops.tech/)
