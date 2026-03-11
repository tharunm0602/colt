resource "google_project" "sbx_project" {
  name       = var.project_name
  project_id = var.project_id
  folder_id  = var.folder_id
  billing_account = var.billing_account
}

resource "google_project_service" "apis" {
  for_each = toset([
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "storage.googleapis.com"
  ])
  project = google_project.sbx_project.project_id
  service = each.key
  disable_on_destroy = false
}
