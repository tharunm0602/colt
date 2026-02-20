module "gcs_bucket" {
  source = "../../../../modules/gcs"

  project_id    = var.project_id
  name          = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
  versioning    = true
  force_destroy = false
  bucket_policy_only = true

  labels = {
    environment = "sbx"
    managed_by  = "terraform"
  }
}
