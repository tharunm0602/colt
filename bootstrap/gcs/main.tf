resource "google_storage_bucket" "state_bucket" {
  project                     = var.project_id
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  
  labels = {
    env = "bootstrap"
  }
}
