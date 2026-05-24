# Terraform configurations for different environments

# Development
locals {
  dev = {
    project_id   = "portfolio-dev-123"
    region       = "us-central1"
    environment  = "dev"
    node_count   = 1
    min_nodes    = 1
    max_nodes    = 2
    machine_type = "e2-small"
    db_tier      = "db-f1-micro"
  }
}

# Staging (GCP Free Tier optimized)
locals {
  staging = {
    project_id   = "portfolio-staging-123"
    region       = "us-central1"
    environment  = "staging"
    node_count   = 1
    min_nodes    = 1
    max_nodes    = 3
    machine_type = "e2-medium"
    db_tier      = "db-f1-micro"
  }
}

# Production
locals {
  prod = {
    project_id   = "portfolio-prod-123"
    region       = "us-central1"
    environment  = "prod"
    node_count   = 3
    min_nodes    = 3
    max_nodes    = 10
    machine_type = "n1-standard-2"
    db_tier      = "db-n1-standard-2"
  }
}
