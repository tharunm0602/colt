variable "folder_id" {
  description = "The folder ID (format: folders/1234)"
  type        = string
}

variable "project_name" {
  description = "Display name of the project"
  type        = string
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "billing_account" {
  description = "Billing Account ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}
