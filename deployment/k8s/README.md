# Kubernetes Deployment Guide

## Overview

Complete K8s manifests for deploying the Portfolio System Architect ecosystem.

### Features

✅ **All 8 Microservices**: Full Deployment + Service + ConfigMap for each app
✅ **PostgreSQL Database**: StatefulSet with persistent storage
✅ **Horizontal Pod Autoscaling (HPA)**: cloud-reason + ml-model-registry scale automatically
✅ **Ingress Routing**: Single entry point for all services
✅ **Network Policies**: Least-privilege security (frontend ↔ backend ↔ DB)
✅ **Kustomize Structure**: base + overlays for dev/staging/prod
✅ **Multi-platform**: GKE v1.27+, Kind, Minikube

---

## Prerequisites

### Required
- Kubernetes 1.27+
- kubectl installed
- kustomize installed (kubectl built-in or standalone)
- Access to container registry (GHCR, DockerHub, etc.)

### Recommended
- Metrics Server (for HPA): `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
- Ingress Controller (NGINX or GCP Load Balancer)

---

## Directory Structure

```
deployment/k8s/
├── base/
│   ├── namespace/          # portfolio namespace
│   ├── postgres/           # PostgreSQL database
│   ├── services/           # 6 microservices (it-compass, cloud-reason, etc.)
│   ├── ingress/            # Ingress + Network Policies
│   └── kustomization.yaml  # base kustomization
├── overlays/
│   ├── dev/               # Local Kind/Minikube (1 replica each)
│   ├── staging/           # GCP GKE Free Tier (2 replicas)
│   └── prod/              # Production GKE (3+ replicas)
└── README.md
```

---

## Deployment Options

### Option 1: Local Development (Kind/Minikube)

#### Step 1: Create local cluster
```bash
# Kind
kind create cluster --name portfolio

# OR Minikube
minikube start --cpus 4 --memory 8192
```

#### Step 2: Deploy with dev overlay
```bash
kubectl apply -k deployment/k8s/overlays/dev
```

#### Step 3: Verify deployment
```bash
kubectl get pods -n portfolio
kubectl get svc -n portfolio
kubectl logs -n portfolio -l app=it-compass
```

#### Step 4: Access services
```bash
# Port-forward to it-compass
kubectl port-forward -n portfolio svc/dev-it-compass 8501:8501

# Visit http://localhost:8501
```

---

### Option 2: GCP GKE Free Tier

#### Step 1: Create GKE cluster
```bash
gcloud container clusters create portfolio-cluster \
  --zone us-central1-a \
  --num-nodes 1 \
  --machine-type g1-small \
  --enable-ip-alias \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 3

# Get credentials
gcloud container clusters get-credentials portfolio-cluster --zone us-central1-a
```

#### Step 2: Install Ingress Controller
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/gcp/deploy.yaml
```

#### Step 3: Create secrets (from GitHub Secrets)
```bash
kubectl create secret generic portfolio-secrets \
  -n portfolio \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  --from-literal=DATABASE_URL=$DATABASE_URL \
  --from-literal=JWT_SECRET=$JWT_SECRET \
  --from-literal=API_KEY_SECRET=$API_KEY_SECRET
```

#### Step 4: Deploy with staging overlay
```bash
kubectl apply -k deployment/k8s/overlays/staging
```

#### Step 5: Configure Ingress
```bash
# Get Load Balancer IP
kubectl get ingress -n portfolio -w

# Update /etc/hosts (or DNS)
echo "<LOAD_BALANCER_IP> portfolio.local" | sudo tee -a /etc/hosts
```

#### Step 6: Access
```bash
http://portfolio.local/it-compass
http://portfolio.local/cloud-reason
http://portfolio.local/ml-registry
```

---

### Option 3: Production GKE

#### Step 1: Create production cluster with HA
```bash
gcloud container clusters create portfolio-prod \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-ip-alias \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-network-policy \
  --addons HttpLoadBalancing,HttpsLoadBalancing
```

#### Step 2: Install monitoring stack
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

#### Step 3: Deploy with prod overlay
```bash
kubectl apply -k deployment/k8s/overlays/prod
```

#### Step 4: Setup SSL/TLS (cert-manager)
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Verification Checklist

```bash
# Check namespace
kubectl get namespace portfolio

# Check all deployments
kubectl get deployments -n portfolio

# Check pods are running
kubectl get pods -n portfolio -o wide

# Check services
kubectl get svc -n portfolio

# Check Ingress
kubectl get ingress -n portfolio

# Check HPA status
kubectl get hpa -n portfolio

# View logs
kubectl logs -n portfolio -l app=cloud-reason -f

# Check resource usage
kubectl top pods -n portfolio
kubectl top nodes
```

---

## Resource Limits

### Dev Environment (GCP Free Tier compatible)
- **Per pod**: 100m CPU / 256Mi memory (typical)
- **Total cluster**: ~1 vCPU / 3.75GB memory (g1-small nodes × 1)

### Staging Environment (GCP Free Tier)
- **Per pod**: 200-500m CPU / 256-512Mi memory
- **Total cluster**: ~2 vCPU / 6GB memory (g1-small × 3 nodes or n1-standard-1)

### Production Environment
- **Per pod**: 200-1000m CPU / 256-2000Mi memory
- **Total cluster**: 6-10 vCPU / 16-32GB memory (n1-standard-2+)

---

## HPA Configuration

### Cloud-Reason (RAG API)
- Min replicas: 2
- Max replicas: 5
- Scale up: when CPU > 70% or Memory > 80%
- Scale down: after 5 minutes of low utilization

### ML-Model-Registry (Model Training/Inference)
- Min replicas: 2
- Max replicas: 4
- Scale up: when CPU > 75% or Memory > 85%
- Scale down: after 5 minutes of low utilization

**To monitor HPA**:
```bash
kubectl get hpa -n portfolio -w
kubectl describe hpa cloud-reason-hpa -n portfolio
```

---

## Network Policies

Implemented least-privilege networking:

| From | To | Port | Allowed |
|------|----|----|---------|
| Ingress | it-compass (Frontend) | 8501 | ✅ |
| Frontend | Backend services | Any | ✅ |
| Backend | PostgreSQL | 5432 | ✅ |
| Backend | Backend | Any | ✅ |
| Prometheus | All pods | 9090 | ✅ |

**To disable network policies** (if needed):
```bash
kubectl delete networkpolicies --all -n portfolio
```

---

## Secret Management

### Create secrets from environment variables
```bash
kubectl create secret generic portfolio-secrets \
  -n portfolio \
  --from-literal=POSTGRES_PASSWORD=$DB_PASSWORD \
  --from-literal=DATABASE_URL=$DB_URL \
  --from-literal=JWT_SECRET=$JWT_SECRET \
  --from-literal=API_KEY_SECRET=$API_KEY
```

### Update secrets
```bash
kubectl set env secret/portfolio-secrets \
  -n portfolio \
  POSTGRES_PASSWORD=$NEW_PASSWORD
```

### View secrets (base64 encoded)
```bash
kubectl get secret portfolio-secrets -n portfolio -o yaml
```

---

## Troubleshooting

### Pods not starting
```bash
# Check events
kubectl describe pod <pod-name> -n portfolio

# Check logs
kubectl logs <pod-name> -n portfolio

# Check resource availability
kubectl top nodes
kubectl describe node <node-name>
```

### Ingress not routing
```bash
# Check Ingress controller pods
kubectl get pods -n ingress-nginx

# Check Ingress rules
kubectl describe ingress portfolio-ingress -n portfolio

# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget http://it-compass:8501
```

### HPA not scaling
```bash
# Ensure metrics-server is running
kubectl get deployment metrics-server -n kube-system

# Check HPA status
kubectl describe hpa cloud-reason-hpa -n portfolio

# View current metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods -n portfolio
```

---

## Common Commands

```bash
# Deploy all services
kubectl apply -k deployment/k8s/overlays/staging

# Delete all resources
kubectl delete -k deployment/k8s/overlays/staging

# Restart a deployment
kubectl rollout restart deployment/it-compass -n portfolio

# Scale manually (overrides HPA)
kubectl scale deployment/cloud-reason --replicas=3 -n portfolio

# Get resource usage
kubectl top pods -n portfolio --sort-by memory

# View deployment history
kubectl rollout history deployment/it-compass -n portfolio

# Rollback to previous version
kubectl rollout undo deployment/it-compass -n portfolio

# Stream logs from all pods
kubectl logs -n portfolio -l app=cloud-reason -f --all-containers=true
```

---

## Grant Compliance Notes

✅ **Scalable architecture**: HPA demonstrates cloud-native scaling
✅ **Multi-environment support**: dev/staging/prod overlays
✅ **Security**: Network policies + non-root users + secret management
✅ **Monitoring ready**: ServiceMonitor placeholders for Prometheus integration
✅ **GCP Free Tier compatible**: Resource limits suitable for free tier
✅ **GitOps ready**: All config in version control via Kustomize

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Guide](https://kustomize.io/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Kind Documentation](https://kind.sigs.k8s.io/)

