module "workbench" {
  source = "../../modules/workbench"

  name              = var.instance_name
  project_id        = var.project_id
  location          = var.location
  machine_type      = var.machine_type
  boot_disk_size_gb = var.boot_disk_size_gb
  boot_disk_type    = var.boot_disk_type

  network_interfaces = [
    {
      network = var.network
      subnet  = var.subnet
    }
  ]
}
