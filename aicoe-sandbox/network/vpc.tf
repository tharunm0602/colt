###########################################
###      AICOE VPC Network             ###
###########################################
resource "google_compute_network" "aicoe_network" {
  name                    = "aicoe-${var.envname}-vpc"
  auto_create_subnetworks = false
}
