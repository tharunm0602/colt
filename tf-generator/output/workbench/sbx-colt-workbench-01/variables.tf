variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "instance_name" {
  description = "Workbench instance name"
  type        = string
}

variable "location" {
  description = "Zone for the instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "e2-medium"
}

variable "network" {
  description = "VPC network name"
  type        = string
}

variable "subnet" {
  description = "Subnet name"
  type        = string
}

variable "boot_disk_size_gb" {
  description = "Boot disk size in GB"
  type        = number
  default     = 150
}

variable "boot_disk_type" {
  description = "Boot disk type"
  type        = string
  default     = "PD_BALANCED"
}
