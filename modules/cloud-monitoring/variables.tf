/**
 * Variables for Cloud Monitoring module
 */

variable "project_id" {
  type        = string
  description = "The project ID where Monitoring resources will be created"
}

variable "cpu_threshold" {
  type        = number
  description = "CPU threshold as percentage (0-1)"
  default     = 0.8
}

variable "notification_channels" {
  type        = list(string)
  description = "Notification channel IDs for CPU alerts"
  default     = []
}