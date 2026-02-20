module "artifact_registry" {
  source = "../../../../modules/artifact-registry"

  project_id    = var.project_id
  repository_id = var.repository_id
  location      = var.location
  format        = var.format
  description   = var.description
  mode          = "STANDARD_REPOSITORY"

  docker_config = {
    immutable_tags = true
  }

  labels = {
    environment = "sbx"
    managed_by  = "terraform"
  }
}
