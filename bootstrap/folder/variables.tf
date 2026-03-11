variable "org_id" {
  description = "The organization ID"
  type        = string
}

variable "folder_name" {
  description = "Name of the sandbox folder"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}
