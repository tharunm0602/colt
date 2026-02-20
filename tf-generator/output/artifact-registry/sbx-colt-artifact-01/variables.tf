variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "repository_id" {
  description = "Repository name"
  type        = string
}

variable "location" {
  description = "Location for the repository"
  type        = string
}

variable "format" {
  description = "Repository format (DOCKER, MAVEN, NPM, PYTHON)"
  type        = string
  default     = "DOCKER"
}

variable "description" {
  description = "Repository description"
  type        = string
  default     = "Artifact Registry Repository"
}
