module "colt_sbx_sa" {
  source = "../../modules/service-account"

  project_id   = var.project_id
  name         = var.sa_name
  display_name = var.display_name

}