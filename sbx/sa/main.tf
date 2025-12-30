module "colt_sbx_sa" {
  source = "colt/modules/service-account"

  project_id   = var.project_id
  name         = "colt-sbx-sa"
  display_name = "Colt Sandbox Service Account"
  description  = "Service account for Colt sandbox workloads"
}