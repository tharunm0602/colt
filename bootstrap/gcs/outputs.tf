output "bucket_name" {
  description = "The name of the GCS bucket"
  value       = google_storage_bucket.state_bucket.name
}

output "bucket_url" {
  description = "The URL of the bucket"
  value       = google_storage_bucket.state_bucket.url
}
