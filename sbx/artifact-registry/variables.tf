variable "project_id" {
  description = "The ID of the project in which the resource belongs."
  type        = string
}

variable "location" {
  description = "The region where the repository will be created."
  type        = string
}

variable "repository_id" {
  description = "The repository name."
  type        = string
}

variable "format" {
  description = "The format of packages that are stored in the repository (DOCKER, MAVEN, NPM, PYTHON, APT, YUM)."
  type        = string
}

variable "description" {
  description = "The user-provided description of the repository."
  type        = string
  default     = "Artifact Registry Repository"
}

variable "kms_key_name" {
  description = "The Cloud KMS resource name of the customer managed encryption key."
  type        = string
  default     = null
}

variable "labels" {
  description = "Labels for the repository."
  type        = map(string)
  default     = {}
}

variable "docker_config" {
  description = "Docker repository config contains repository level configuration for the repositories of docker type"
  type = object({
    immutable_tags = optional(bool)
  })
  default = null
}
