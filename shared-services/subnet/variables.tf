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

variable "subnets" {
  type = list(object({
    subnet_name           = string
    subnet_ip             = string
    subnet_region         = string
    subnet_private_access = optional(string, "false")
  }))
  description = "The list of subnets being created"
}
