variable "project_id" {
  description = "The ID of the project."
  type        = string
}

variable "region" {
  description = "The region."
  type        = string
}

variable "network_name" {
  description = "The name of the network."
  type        = string
}

variable "routing_mode" {
  description = "The network routing mode."
  type        = string
  default     = "GLOBAL"
}
