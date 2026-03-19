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
