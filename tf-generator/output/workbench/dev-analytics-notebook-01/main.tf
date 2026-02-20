module "workbench" {
  source = "../../../../modules/workbench"

  project_id        = var.project_id
  name              = var.instance_name
  location          = var.location
  machine_type      = var.machine_type
  boot_disk_size_gb = var.boot_disk_size_gb
  boot_disk_type    = var.boot_disk_type
  disable_public_ip = true
  disk_encryption   = "GMEK"

  network_interfaces = [{
    network  = var.network
    subnet   = var.subnet
    nic_type = "VIRTIO_NET"
  }]

  labels = {
    environment = "sbx"
    managed_by  = "terraform"
  }
}
