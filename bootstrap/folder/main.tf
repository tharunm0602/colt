resource "google_folder" "sandbox" {
  display_name = var.folder_name
  parent       = "organizations/${var.org_id}"
}

output "folder_id" {
  value = google_folder.sandbox.name
}
