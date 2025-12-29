module "vpc" {
  source  = "colt/modules/vpc/"
  
  project_id   = var.project_id
  network_name = var.vpc_name
  mtu          = var.mtu
  routing_mode = "REGIONAL"
  enable_ipv6_ula = false 
  shared_vpc_host = false
  bgp_best_path_selection_mode = "STANDARD"
}
