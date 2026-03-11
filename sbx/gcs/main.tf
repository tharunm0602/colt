module "gcs_bucket" {
  source     = "../../modules/gcs"
  project_id = var.project_id
  name       = var.bucket_name
  location   = var.region

  versioning             = true
  bucket_policy_only     = true # This maps to uniform_bucket_level_access in the module if it's the standard GCS module
  labels                 = var.labels
}
