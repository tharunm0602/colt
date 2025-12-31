module "colt_sbx_sa" {
  source = "../../modules/service-account"

  project_id   = var.project_id
  name         = var.sa_name
  display_name = var.display_name

project_roles = [
  "roles/logging.logWriter",
  "roles/monitoring.editor",
  "roles/iam.serviceAccountUser",
  roles/storage.admin",
  "roles/aiplatform.user"
]
}