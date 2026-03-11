variable "folder_id" {
  description = "The folder ID (format: folders/1234)"
  type        = string
}

variable "viewer_members" {
  description = "List of members to grant viewer role at folder level (e.g., user:email@example.com, group:team@example.com, serviceAccount:sa@project.iam.gserviceaccount.com)"
  type        = list(string)
  default     = []
}

variable "custom_role_bindings" {
  description = "Map of custom role bindings {binding_name = {role = 'roles/xxx', member = 'user:xxx'}}"
  type = map(object({
    role   = string
    member = string
  }))
  default = {}
}

variable "region" {
  description = "GCP region"
  type        = string
}
