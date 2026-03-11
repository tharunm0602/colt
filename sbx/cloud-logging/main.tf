module "cloud_logging_api" {
  source     = "../../modules/cloud-logging"
  project_id = var.project_id
}
