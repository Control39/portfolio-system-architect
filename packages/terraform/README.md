# Terraform for GCP Free Tier Deployment

## Prerequisites

```bash
# 1. Install Terraform
brew install terraform  # or download from terraform.io

# 2. Install Google Cloud SDK
brew install google-cloud-sdk

# 3. Authenticate
gcloud auth application-default login

# 4. Set project
gcloud config set project portfolio-dev-123
```

## Deployment

### Development Environment (Free Tier)

```bash
# Initialize Terraform
cd packages/terraform
terraform init

# Review plan
terraform plan -var-file="dev.tfvars"

# Apply
terraform apply -var-file="dev.tfvars"

# Get outputs
terraform output
```

### Staging Environment

```bash
terraform plan -var-file="staging.tfvars"
terraform apply -var-file="staging.tfvars"
```

### Production Environment

```bash
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"
```

## Terraform Variables (create terraform.tfvars)

```hcl
project_id   = "my-gcp-project-id"
region       = "us-central1"
environment  = "dev"  # or staging, prod
db_password  = "secure-random-password"
```

## Remote State Setup

```bash
# Create GCS bucket for state
gsutil mb gs://portfolio-terraform-state-${PROJECT_ID}

# Enable versioning
gsutil versioning set on gs://portfolio-terraform-state-${PROJECT_ID}

# Update backend in main.tf to use bucket
terraform init
```

## What Gets Created

### Network
- VPC network (portfolio-vpc)
- Subnet with Cloud Logging enabled

### Kubernetes (GKE)
- GKE Cluster (1-3 nodes depending on environment)
- Auto-scaling node pool
- Network policies enabled
- Workload Identity enabled
- Logging & monitoring enabled

### Database
- CloudSQL PostgreSQL 14
- Private IP (CloudSQL Auth Proxy)
- Automated backups
- Query Insights enabled

### Container Registry
- Artifact Registry for Docker images
- Private repository

### Storage
- GCS bucket for backups with versioning

### IAM
- Service Account for workloads
- Role bindings for Artifact Registry, CloudSQL, Workload Identity

## Costs (Free Tier)

- **GKE Cluster**: FREE (pay for nodes only)
- **Node (e2-small)**: ~$10-15/month
- **CloudSQL (db-f1-micro)**: FREE first instance, then ~$8/month
- **Artifact Registry**: FREE for first 500MB/month
- **GCS Storage**: FREE first 5GB/month

**Total for Dev**: ~$15-20/month
**Total for Prod**: ~$50-100/month

## Destroy Resources

```bash
# List resources
terraform state list

# Destroy specific resource (careful!)
terraform destroy -target=google_compute_network.portfolio_vpc

# Destroy all
terraform destroy -var-file="dev.tfvars"
```

## Troubleshooting

### Error: "google_sql_database_instance" is forbidden

**Solution**: Enable Cloud SQL Admin API
```bash
gcloud services enable sqladmin.googleapis.com
```

### Error: "compute resource is forbidden"

**Solution**: Enable Compute Engine API
```bash
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
```

### State Lock Issues

```bash
# Force unlock (USE WITH CAUTION)
terraform force-unlock <lock-id>
```

## References

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP Free Tier](https://cloud.google.com/free/docs/gcp-free-tier)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
