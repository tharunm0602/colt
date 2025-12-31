module "artifact_registry" {
  source = "../../modules/artifact-registry"

  project_id    = var.project_id
  location      = var.location
  repository_id = var.repository_id
  format        = var.format
  description   = var.description
  kms_key_name  = var.kms_key_name
  labels        = var.labels
  docker_config = var.docker_config
}
