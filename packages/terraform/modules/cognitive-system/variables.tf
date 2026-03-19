variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-medium"
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
  default     = 3
}

variable "preemptible" {
  description = "Use preemptible nodes"
  type        = bool
  default     = false
}

variable "arch_compass_tag" {
  description = "Tag for ArchCompass"
  type        = string
  default     = "arch-compass"
}
