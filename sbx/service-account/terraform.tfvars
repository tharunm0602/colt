project_id   = "cloud-practice-dev-2"
region       = "us-central1"
sa_name      = "sbx-terraform-sa"
display_name = "Sandbox Terraform Service Account"
project_roles = [
  "roles/viewer",
  "roles/storage.objectViewer"
]
