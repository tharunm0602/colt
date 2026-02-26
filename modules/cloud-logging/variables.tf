/**
 * Variables for Cloud Logging module
 */

variable "project_id" {
  type        = string
  description = "The project ID where Logging resources will be created"
}

variable "sink_name" {
  type        = string
  description = "Name of the logging sink"
}

variable "destination" {
  type        = string
  description = "Destination type for the sink: storage"
}

variable "log_filter" {
  type        = string
  description = "Filters to apply to log"
  default     = ""
}