variable "project_id" {
  description = "The ID of the project."
  type        = string
}

variable "region" {
  description = "The region."
  type        = string
}

variable "sa_name" {
  description = "Name of the service account"
  type        = string
}

variable "display_name" {
  description = "Display name of the service account"
  type        = string
}

variable "project_roles" {
  description = "Roles for the service account"
  type        = list(string)
}
