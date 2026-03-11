resource "google_service_account" "bootstrap_sa" {
  project      = var.project_id
  account_id   = var.sa_name
  display_name = var.display_name
}
