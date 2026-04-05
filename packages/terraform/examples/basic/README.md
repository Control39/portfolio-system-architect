# Basic Terraform Example

## Basic Terraform Example for Cognitive System GKE

### Prerequisites
- GCP project with GKE API enabled
- terraform CLI
- GCP credentials (gcloud auth application-default login)

### Usage
1. terraform init
2. terraform plan -var="project_id=your-gcp-project" -var="region=us-central1"
3. terraform apply -var="project_id=your-gcp-project"

### Variables
- project_id: GCP project ID
- region: GKE region (default us-central1)
- machine_type: Node pool machine (default e2-medium)

### Outputs
- cluster_name
- endpoint

Requires GCP credentials.

