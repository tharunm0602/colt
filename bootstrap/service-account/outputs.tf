output "service_account_email" {
  description = "The email address of the service account"
  value       = google_service_account.bootstrap_sa.email
}

output "service_account_id" {
  description = "The fully qualified ID of the service account"
  value       = google_service_account.bootstrap_sa.id
}

output "service_account_name" {
  description = "The fully qualified name of the service account"
  value       = google_service_account.bootstrap_sa.name
}
