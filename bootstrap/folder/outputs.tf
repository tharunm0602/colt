output "folder_id" {
  description = "The folder ID in the format folders/123456789"
  value       = google_folder.sandbox.name
}

output "folder_name" {
  description = "The display name of the folder"
  value       = google_folder.sandbox.display_name
}
