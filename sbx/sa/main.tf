module "colt_sbx_sa" {
  source = "../../modules/service-account"

  project_id    = var.project_id
  name          = var.sa_name
  display_name  = var.display_name
  project_roles = var.project_roles
}

resource "google_project_iam_member" "roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.editor",
    "roles/storage.admin",
    "roles/iam.serviceAccountUser",
    "roles/aiplatform.user"
])
  project  = var.project_id
  role     = each.value
  member   = google_service_account.sa.member
}