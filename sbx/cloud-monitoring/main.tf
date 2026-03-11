module "cloud_monitoring_api" {
  source     = "../../modules/cloud-monitoring"
  project_id = var.project_id
}
