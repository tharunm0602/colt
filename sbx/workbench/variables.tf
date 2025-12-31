variable "project_id" {
  description = "The ID of the project in which the resource belongs."
  type        = string
}

variable "location" {
  description = "The zone where the instance will be created."
  type        = string
}

variable "instance_name" {
  description = "The name of the workbench instance."
  type        = string
}

variable "machine_type" {
  description = "The machine type of the instance."
  type        = string
  default     = "e2-medium"
}

variable "network" {
  description = "The network to attach the instance to."
  type        = string
}

variable "subnet" {
  description = "The subnetwork to attach the instance to."
  type        = string
}

variable "boot_disk_size_gb" {
  description = "The size of the boot disk in GB."
  type        = number
  default     = 100
}

variable "boot_disk_type" {
  description = "The type of the boot disk."
  type        = string
  default     = "PD_SSD"
}
