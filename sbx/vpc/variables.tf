variable "project_id" {
  description = "GCP Project ID where the VPC will be created"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "mtu" {
  description = "MTU size for the VPC network"
  type        = number
  default     = 1460
}

variable "enable_ipv6_ula" {
  type    = bool
  default = false
}
