module "subnet" {
  source       = "../../modules/subnet"
  project_id   = var.project_id
  network_name = var.network_name
  subnets      = var.subnets
}
