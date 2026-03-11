resource "google_iam_workload_identity_pool" "pool" {
  project                   = var.project_id
  workload_identity_pool_id = var.pool_id
  display_name              = "Azure DevOps Pool"
}

resource "google_iam_workload_identity_pool_provider" "provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.provider_id
  display_name                       = "Azure DevOps Provider"
  
  attribute_mapping = {
    "google.subject" = "assertion.sub"
  }
  
  oidc {
    issuer_uri = "https://vstoken.dev.azure.com/${var.azure_org}"
  }
}

resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = var.sa_id
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.pool.name}/subject/${var.azure_subject}"
}
