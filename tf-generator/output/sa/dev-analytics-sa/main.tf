module "service_account" {
  source = "../../../../modules/service-account"

  project_id    = var.project_id
  name          = var.sa_name
  display_name  = var.display_name

  project_roles = [
    "roles/dataproc.worker",
    "roles/pubsub.subscriber",
    "roles/storage.objectViewer"
  ]
}
