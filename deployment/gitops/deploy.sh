#!/bin/bash
set -e

# Simple GitOps deploy script
# Usage: ./deploy.sh [overlay]
# overlay can be dev, staging, prod (default: staging)

OVERLAY=${1:-staging}
K8S_PATH="deployment/k8s/overlays/${OVERLAY}"

echo "Deploying Portfolio System with overlay: ${OVERLAY}"
echo "Kustomize path: ${K8S_PATH}"

# Apply kustomize
kubectl apply -k "${K8S_PATH}"

# Wait for deployments
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/it-compass -n portfolio --timeout=300s
kubectl rollout status deployment/decision-engine -n portfolio --timeout=300s
kubectl rollout status deployment/ml-model-registry -n portfolio --timeout=300s
kubectl rollout status deployment/portfolio-organizer -n portfolio --timeout=300s
kubectl rollout status deployment/system-proof -n portfolio --timeout=300s
kubectl rollout status deployment/auth-service -n portfolio --timeout=300s
kubectl rollout status deployment/infra-orchestrator -n portfolio --timeout=300s
kubectl rollout status deployment/career-development -n portfolio --timeout=300s

echo "All deployments are ready."
echo "Services:"
kubectl get svc -n portfolio
echo "Pods:"
kubectl get pods -n portfolio
