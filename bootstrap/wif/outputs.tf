output "workload_identity_pool_id" {
  description = "The ID of the workload identity pool"
  value       = google_iam_workload_identity_pool.pool.workload_identity_pool_id
}

output "workload_identity_pool_name" {
  description = "The fully qualified name of the workload identity pool"
  value       = google_iam_workload_identity_pool.pool.name
}

output "workload_identity_provider_id" {
  description = "The ID of the workload identity provider"
  value       = google_iam_workload_identity_pool_provider.provider.workload_identity_pool_provider_id
}

output "workload_identity_provider_name" {
  description = "The fully qualified name of the workload identity provider"
  value       = google_iam_workload_identity_pool_provider.provider.name
}
