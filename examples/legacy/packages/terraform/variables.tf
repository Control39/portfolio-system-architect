# Variables for Portfolio System Architect Terraform

variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP Region"
}

variable "environment" {
  type        = string
  description = "Environment (dev, staging, prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "subnet_cidr" {
  type        = string
  default     = "10.0.0.0/24"
  description = "Subnet CIDR range"
}

# GKE
variable "node_count" {
  type        = number
  default     = 1
  description = "Initial number of nodes in GKE cluster"
}

variable "min_node_count" {
  type        = number
  default     = 1
  description = "Minimum nodes in node pool"
}

variable "max_node_count" {
  type        = number
  default     = 3
  description = "Maximum nodes in node pool"
}

variable "machine_type" {
  type        = string
  default     = "e2-medium"
  description = "GKE node machine type"
}

# CloudSQL
variable "db_tier" {
  type        = string
  default     = "db-f1-micro"
  description = "CloudSQL tier (db-f1-micro for Free Tier)"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "PostgreSQL password (use terraform.tfvars or environment variable)"
}
