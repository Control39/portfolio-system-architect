# Terraform Configuration for Portfolio System Architect
# Production-ready infrastructure for GCP

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Remote backend for state management
  backend "gcs" {
    bucket = "portfolio-terraform-state"
    prefix = "production"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "portfolio_vpc" {
  name                    = "portfolio-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

# Subnet for GKE
resource "google_compute_subnetwork" "portfolio_subnet" {
  name          = "portfolio-subnet-${var.environment}"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.portfolio_vpc.id

  private_ip_google_access = true
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_logs_enabled    = true
    sampling_rate        = 0.5
  }
}

# GKE Cluster
resource "google_container_cluster" "portfolio_gke" {
  name     = "portfolio-gke-${var.environment}"
  location = var.region

  initial_node_count       = var.node_count
  remove_default_node_pool = true

  network    = google_compute_network.portfolio_vpc.name
  subnetwork = google_compute_subnetwork.portfolio_subnet.name

  # Network Policy enabled
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Logging & Monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  # Master Authorized Networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "Allow all"
    }
  }
}

# Node Pool
resource "google_container_node_pool" "portfolio_nodes" {
  name           = "portfolio-pool-${var.environment}"
  location       = var.region
  cluster        = google_container_cluster.portfolio_gke.name
  node_count     = var.node_count
  max_node_count = var.max_node_count
  min_node_count = var.min_node_count

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  node_config {
    preemptible  = var.environment == "dev" ? true : false
    machine_type = var.machine_type

    disk_size_gb = 50
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    tags = ["portfolio", var.environment]

    labels = {
      environment = var.environment
      managed_by  = "terraform"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# CloudSQL (PostgreSQL)
resource "google_sql_database_instance" "portfolio_postgres" {
  name             = "portfolio-postgres-${var.environment}"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      private_network = google_compute_network.portfolio_vpc.id
      require_ssl     = true
      ipv4_enabled    = false
    }

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }
  }

  deletion_protection = var.environment == "prod" ? true : false
}

# PostgreSQL Database
resource "google_sql_database" "portfolio_db" {
  name     = "portfolio"
  instance = google_sql_database_instance.portfolio_postgres.name
  charset  = "UTF8"
}

# Database User
resource "google_sql_user" "portfolio_user" {
  name     = "portfolio"
  instance = google_sql_database_instance.portfolio_postgres.name
  type     = "BUILT_IN"
  password = var.db_password
}

# Artifact Registry (Docker images)
resource "google_artifact_registry_repository" "portfolio_repo" {
  location      = var.region
  repository_id = "portfolio-${var.environment}"
  description   = "Portfolio System Architect Docker images"
  format        = "DOCKER"
}

# Service Account for K8s workloads
resource "google_service_account" "portfolio_sa" {
  account_id   = "portfolio-${var.environment}"
  display_name = "Portfolio System Architect SA"
  description  = "Service account for portfolio microservices"
}

# IAM Binding: Artifact Registry access
resource "google_artifact_registry_repository_iam_member" "portfolio_docker_access" {
  location   = google_artifact_registry_repository.portfolio_repo.location
  repository = google_artifact_registry_repository.portfolio_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.portfolio_sa.email}"
}

# IAM Binding: CloudSQL Client
resource "google_project_iam_member" "portfolio_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.portfolio_sa.email}"
}

# IAM Binding: Workload Identity
resource "google_service_account_iam_member" "portfolio_workload_identity" {
  service_account_id = google_service_account.portfolio_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[portfolio/portfolio-ksa]"
}

# Storage Bucket for backups
resource "google_storage_bucket" "portfolio_backups" {
  name          = "portfolio-backups-${var.project_id}-${var.environment}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type          = "Delete"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }

  public_access_prevention = "enforced"
}

# Outputs
output "gke_cluster_name" {
  value       = google_container_cluster.portfolio_gke.name
  description = "GKE Cluster name"
}

output "gke_cluster_endpoint" {
  value       = google_container_cluster.portfolio_gke.endpoint
  description = "GKE Cluster endpoint"
  sensitive   = true
}

output "cloudsql_connection_name" {
  value       = google_sql_database_instance.portfolio_postgres.connection_name
  description = "CloudSQL connection name (for Kubernetes)"
}

output "artifact_registry_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.portfolio_repo.name}"
  description = "Artifact Registry URL"
}

output "backup_bucket" {
  value       = google_storage_bucket.portfolio_backups.name
  description = "GCS bucket for backups"
}
