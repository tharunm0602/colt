variable "project_id" {
  description = "The ID of the project to create the bucket in."
  type        = string
}

variable "region" {
  description = "The region for the resources."
  type        = string
}

variable "bucket_name" {
  description = "The name of the bucket."
  type        = string
}

variable "labels" {
  description = "Labels for the bucket."
  type        = map(string)
  default     = {
    env = "sandbox"
  }
}
