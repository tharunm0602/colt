module "artifact_registry" {
  source        = "../../modules/artifact-registry"
  project_id    = var.project_id
  repository_id = var.repository_id
  location      = var.location
  format        = var.format
}
