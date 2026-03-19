output "cluster_name" {
  value       = google_container_cluster.cognitive_system.name
  description = "GKE cluster name"
}

output "endpoint" {
  value       = google_container_cluster.cognitive_system.endpoint
  description = "Cluster endpoint"
}

output "node_pool_name" {
  value = google_container_node_pool.primary_nodes.name
}
