# Kubernetes Sealed Secrets Configuration
# This example shows how to manage secrets securely in K8s

---
# 1. Secret manifest (before sealing)
# DO NOT COMMIT THIS FILE IN PRODUCTION
# This is for reference only

apiVersion: v1
kind: Secret
metadata:
  name: portfolio-secrets
  namespace: portfolio
type: Opaque
stringData:
  # Database
  POSTGRES_DB: portfolio
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: ${DB_PASSWORD}  # Will be injected from GitHub Secrets
  
  # JWT & API Security
  JWT_SECRET: ${JWT_SECRET}
  API_KEY_SECRET: ${API_KEY_SECRET}
  
  # Optional: Cloud credentials (for prod deployment)
  # GCP_CREDENTIALS: ${GCP_CREDENTIALS_JSON}
  # AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  # AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}

---
# 2. To seal this secret, use:
# kubeseal -f secret.yaml -w sealed-secret.yaml
#
# Then commit sealed-secret.yaml (it's safe - encrypted with cluster key)
# 
# Prerequisites:
# - Install Sealed Secrets controller: https://github.com/bitnami-labs/sealed-secrets
# - kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

---
# 3. Example of sealed secret (encrypted output)
# Replace this with your actual sealed secret

apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: portfolio-secrets
  namespace: portfolio
spec:
  encryptedData:
    POSTGRES_DB: AgBXZz4wAAAAAAAA...  # Sealed value (unique per cluster)
    POSTGRES_USER: AgBXZz4wAAAAAAAA...
    POSTGRES_PASSWORD: AgBXZz4wAAAAAAAA...
    JWT_SECRET: AgBXZz4wAAAAAAAA...
    API_KEY_SECRET: AgBXZz4wAAAAAAAA...
  template:
    metadata:
      name: portfolio-secrets
      namespace: portfolio
    type: Opaque

---

# 4. GitHub Actions Integration

To automate secret updates in CI/CD, create a GitHub Actions workflow that uses `kubeseal` to generate sealed secrets from GitHub Secrets.

Example workflow `.github/workflows/secrets.yaml`:

```yaml
name: Update Sealed Secrets
on:
  push:
    branches: [ main ]
    paths:
      - 'deployment/secrets/secret.example.yaml'
  workflow_dispatch:

jobs:
  seal-secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install kubeseal
        run: |
          wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/kubeseal-0.18.0-linux-amd64.tar.gz
          tar -xzf kubeseal-0.18.0-linux-amd64.tar.gz
          sudo mv kubeseal /usr/local/bin/
      - name: Create secret manifest from environment variables
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
          API_KEY_SECRET: ${{ secrets.API_KEY_SECRET }}
        run: |
          envsubst < deployment/secrets/secret.example.yaml > secret.yaml
      - name: Seal secret
        run: |
          kubeseal --cert https://raw.githubusercontent.com/bitnami-labs/sealed-secrets/main/controller.crt -f secret.yaml -w sealed-secret.yaml
      - name: Commit sealed secret
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          mv sealed-secret.yaml deployment/secrets/sealed-secrets/portfolio-secrets.yaml
          git add deployment/secrets/sealed-secrets/portfolio-secrets.yaml
          git commit -m "Update sealed secret [skip ci]" || echo "No changes to commit"
          git push
```

---

# 5. Security Best Practices

- **Never commit unencrypted secrets** – Use `.gitignore` to exclude `secret.yaml` and `*.local.env`.
- **Rotate secrets regularly** – Use Kubernetes CronJob to rotate secrets and update sealed secrets.
- **Limit access to sealed secrets** – Use RBAC to restrict who can create/update SealedSecret resources.
- **Audit secret usage** – Enable Kubernetes audit logs and monitor access to secrets.
- **Use separate namespaces** – Isolate secrets per environment (dev, staging, prod).

---

# 6. Troubleshooting

- If sealed secret fails to decrypt, ensure the Sealed Secrets controller is running in the cluster.
- Verify the controller's public key matches the one used for sealing.
- Check namespace matches the one specified in the sealed secret.
- Use `kubectl get sealedsecret -n portfolio` to inspect sealed secrets.
