variable "project_id" {
  description = "The project ID"
  type        = string
}

variable "pool_id" {
  description = "WIF Pool ID"
  type        = string
}

variable "provider_id" {
  description = "WIF Provider ID"
  type        = string
}

variable "azure_org" {
  description = "Azure DevOps Organization name"
  type        = string
}

variable "azure_subject" {
  description = "Azure DevOps OIDC Subject (sc://org/project/service-connection)"
  type        = string
}

variable "sa_id" {
  description = "Service account resource ID (full name)"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}
