# Secrets Management Strategy
# Production-grade secret handling for Portfolio System Architect

## Overview

This document describes how to securely manage secrets across development, staging, and production environments using industry-standard tools.

## Secret Detection

To prevent accidental leakage of secrets into version control, we use automated scanning with `detect-secrets`.

### Installation

```bash
pip install detect-secrets
```

### Usage

Run a one-time scan to find potential secrets:

```bash
python scripts/security/scan_secrets.py --scan
```

Create a baseline file to whitelist known false positives:

```bash
python scripts/security/scan_secrets.py --create-baseline
```

Audit the baseline (interactive review):

```bash
python scripts/security/scan_secrets.py --audit
```

### Integration with Pre‑commit

Add to `.pre‑commit‑config.yaml`:

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: '\.secrets\.baseline$'
```

### CI/CD Integration

In GitHub Actions, add a step:

```yaml
- name: Detect secrets
  run: |
    pip install detect-secrets
    python scripts/security/scan_secrets.py --scan
```

## Local Development

### Using .env files

```bash
# 1. Copy template
cp .env.example .env.local

# 2. Fill with dev values
cat .env.local
POSTGRES_PASSWORD=dev_password_123
JWT_SECRET=dev_jwt_key_xyz

# 3. Load in docker-compose
docker compose --env-file .env.local up
```

**Never commit .env or .env.local to git**

## GitHub Actions CI/CD

### Setting Repository Secrets

1. Go to: Settings → Secrets and variables → Actions
2. Add secrets:
   - `POSTGRES_PASSWORD`
   - `JWT_SECRET`
   - `API_KEY_SECRET`
   - `TELEGRAM_BOT_TOKEN`
   - `CODECOV_TOKEN`

### Usage in Workflows

```yaml
env:
  DATABASE_URL: postgresql://user:${{ secrets.POSTGRES_PASSWORD }}@postgres:5432/portfolio
```

## Kubernetes: Sealed Secrets

### Installation

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# Install sealing key
kubectl -n kube-system get secrets -o wide
```

### Creating Sealed Secrets

```bash
# 1. Create plain secret
kubectl create secret generic portfolio-secrets \
  -n portfolio \
  --from-literal=POSTGRES_PASSWORD=$DB_PASSWORD \
  --from-literal=JWT_SECRET=$JWT_SECRET \
  --dry-run=client \
  -o yaml > secret.yaml

# 2. Seal the secret
kubeseal -f secret.yaml -w sealed-secret.yaml

# 3. Commit sealed-secret.yaml (encrypted)
git add sealed-secret.yaml
git commit -m "chore: add sealed secrets for production"

# 4. Deploy
kubectl apply -f sealed-secret.yaml
```

## HashiCorp Vault (Advanced)

### Setup

```bash
# Start Vault locally
docker run -d \
  --name vault \
  -e VAULT_DEV_ROOT_TOKEN_ID=mytoken \
  -p 8200:8200 \
  vault:latest

# Enable KV secrets
vault secrets enable -version=2 kv

# Create secrets
vault kv put kv/portfolio/production \
  db_password=$POSTGRES_PASSWORD \
  jwt_secret=$JWT_SECRET
```

### Access in Applications

```python
import hvac

client = hvac.Client(url='http://vault:8200', token='mytoken')
secret = client.secrets.kv.read_secret_version(path='portfolio/production')
db_password = secret['data']['data']['db_password']
```

## AWS Secrets Manager (Production)

### Create Secret

```bash
aws secretsmanager create-secret \
  --name portfolio/production \
  --secret-string '{
    "db_password": "'$POSTGRES_PASSWORD'",
    "jwt_secret": "'$JWT_SECRET'"
  }'
```

### Access in Code

```python
import boto3
import json

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='portfolio/production')
secret = json.loads(response['SecretString'])
```

### IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:portfolio/*"
    }
  ]
}
```

## GCP Secret Manager (Production)

### Create Secret

```bash
gcloud secrets create portfolio-db-password \
  --replication-policy="automatic" \
  --data-file=- <<< "$POSTGRES_PASSWORD"

gcloud secrets create portfolio-jwt-secret \
  --replication-policy="automatic" \
  --data-file=- <<< "$JWT_SECRET"
```

### Access in Code

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
secret_name = "projects/PROJECT_ID/secrets/portfolio-db-password/versions/latest"
response = client.access_secret_version(request={"name": secret_name})
password = response.payload.data.decode('UTF-8')
```

### Workload Identity (K8s)

```bash
# Bind K8s service account to GCP service account
gcloud iam service-accounts add-iam-policy-binding \
  portfolio-workload@PROJECT_ID.iam.gserviceaccount.com \
  --role roles/secretmanager.secretAccessor \
  --member "serviceAccount:portfolio-workload@PROJECT_ID.iam.gserviceaccount.com"

# Annotate K8s service account
kubectl annotate serviceaccount portfolio-ksa \
  -n portfolio \
  iam.gke.io/gcp-service-account=portfolio-workload@PROJECT_ID.iam.gserviceaccount.com
```

## Secret Rotation

### Automated Rotation

```bash
# AWS Secrets Manager
aws secretsmanager rotate-secret \
  --secret-id portfolio/production \
  --rotation-rules AutomaticallyAfterDays=30

# GCP (manual — requires Lambda/Cloud Function)
gcloud secrets versions list portfolio-db-password
```

### Application Reload

```python
# Watch for secret changes and reload
import os
from pathlib import Path

SECRET_FILE = Path("/var/run/secrets/portfolio/db_password")

def get_db_password():
    # Automatically picks up latest version
    return SECRET_FILE.read_text().strip()

# In FastAPI startup
@app.on_event("startup")
async def startup():
    global DB_PASSWORD
    DB_PASSWORD = get_db_password()
```

## Best Practices

✅ **DO:**
- Store secrets in external systems (Vault, AWS Secrets, GCP Secret Manager)
- Rotate secrets regularly (30-90 days)
- Use separate secrets for each environment
- Audit access to secrets
- Use short-lived credentials (STS tokens)
- Seal secrets before committing to git

❌ **DON'T:**
- Store secrets in .env files in git
- Hardcode secrets in code
- Use same secret across environments
- Share secrets via Slack/email
- Store secrets in config files
- Log secrets in stdout/stderr

## Monitoring & Alerts

```yaml
# Prometheus alert for secret access
- alert: UnauthorizedSecretAccess
  expr: increase(secretmanager_access_unauthorized[5m]) > 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Unauthorized secret access detected"
```

## References

- HashiCorp Vault: https://www.vaultproject.io/
- AWS Secrets Manager: https://docs.aws.amazon.com/secretsmanager/
- GCP Secret Manager: https://cloud.google.com/secret-manager/docs
- Sealed Secrets: https://github.com/bitnami-labs/sealed-secrets
