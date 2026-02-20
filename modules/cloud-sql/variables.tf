/**
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# Core Instance Configuration
variable "project_id" {
  type        = string
  description = "The project ID where the Cloud SQL instance will be created"
}

variable "instance_name" {
  type        = string
  description = "The name of the Cloud SQL instance"
}

variable "database_version" {
  type        = string
  description = "The database version (e.g., MYSQL_8_0, POSTGRES_15, SQLSERVER_2019_ENTERPRISE)"
  default     = "POSTGRES_15"
}

variable "region" {
  type        = string
  description = "The region of the Cloud SQL instance (e.g., us-central1, us-east1)"
}

variable "deletion_protection" {
  type        = bool
  description = "Enable deletion protection for the instance"
  default     = true
}

# Instance Configuration
variable "instance_tier" {
  type        = string
  description = "The machine type to use (e.g., db-custom-4-16384, db-f1-micro, db-g1-small)"
  default     = "db-f1-micro"
}

variable "availability_type" {
  type        = string
  description = "The availability type of the instance. High availability (REGIONAL) or standard (ZONAL)"
  default     = "ZONAL"
}

variable "disk_type" {
  type        = string
  description = "The disk type of the instance (PD_SSD or PD_HDD)"
  default     = "PD_SSD"
}

variable "disk_size_gb" {
  type        = number
  description = "The disk size in GB"
  default     = 100
}

variable "backup_enabled" {
    type    = bool
    default = true
}

variable "backup_start_time" {
    type = string
    default = "03:00"
}

variable "point_in_time_recovery_enabled" {
    type    = bool
    default = true
}

variable "enable_public_ip" {
    type        = bool
    default     = false
    description = "Enable public IP"
}

variable "private_network" {
    type        = string
    default     = null
    description = "VPC self link for private IP"
}

variable "require_ssl" {
    type        = bool
    default     = true
    description = "Require SSL connections"
}

variable "maintenance_day" {
    type    = number
    default = 7
}

variable "maintenance_hour" {
    type    = number
    default = 3
}

# Database Configuration
variable "database_flags" {
  type        = list(object({
        name  = string
        value = string
  }))
  description = "List of database names to create"
  default     = []
}

variable "labels" {
    type    = map(string)
    default = {}
}
 
variable "create_default_database" {
    type        = bool
    default     = false
    description =  "Creating default database"
}

variable "default_database_name" {
    type        = string
    default     = "abb"
    description = "Name of the default database"
}

variable "create_default_user" {
    type        = bool
    default     = false
    description = "Creating default user"
}

variable "default_user_name" {
    type        = string
    default     = "app user"
    description = "Name of the default user"
}

variable "default_user_password" {
    type        = string
    sensitive   = true
    default     = null
    description = "Default User Password"
}