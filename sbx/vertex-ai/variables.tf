variable "project_id" {
  description = "The ID of the project."
  type        = string
}

variable "region" {
  description = "The region."
  type        = string
}

variable "vertex_ai_users" {
  description = "List of users to be granted Vertex AI user role"
  type        = list(string)
  default     = []
}
