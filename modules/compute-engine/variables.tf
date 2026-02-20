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
  description = "The project ID where the Compute Engine instance will be created"
}

variable "instance_name" {
  type        = string
  description = "Name of the VM instance"
}

variable "zone" {
  type        = string
  description = "The GCP zone where the instance will be created (e.g., us-central1-a)"
}

variable "machine_type" {
  type        = string
  description = "The machine type to create (e.g., n1-standard-1, e2-medium, n2-highmem-4)"
  default     = "n1-standard-1"
}

variable "boot_disk_image" {
  type        = string
  description = "The image from which to initialize this disk (e.g., debian-cloud/debian-11, ubuntu-os-cloud/ubuntu-2204-lts)"
  default     = "debian-cloud/debian-11"
}

variable "boot_disk_size" {
  type        = number
  description = "The size of the boot disk in GB"
  default     = 50
}

variable "boot_disk_type" {
  type        = string
  description = "The GCE disk type (PD_STANDARD, PD_BALANCED, PD_SSD, PD_EXTREME)"
  default     = "PD_STANDARD"
}

# Networking
variable "network" {
  type        = string
  description = "The name or self_link of the network to attach this interface to"
}

variable "subnetwork" {
  type        = string
  description = "The name or self_link of the subnetwork to which this instance is attached"
  default     = null
}

variable "enable_public_ip" {
  type        = bool
  description = "Enable public IP on the instance"
  default     = false
}

# Service Account
variable "service_account_email" {
  type        = string
  description = "The service account email to attach to the instance. If not provided, the default Compute Engine service account is used"
}

variable "service_account_scopes" {
  type        = list(string)
  description = "List of scopes for the service account (e.g., cloud-platform, storage-full, etc.)"
  default     = ["https://www.googleapis.com/auth/cloud-platform"]
}

# Metadata
variable "metadata" {
  type        = map(string)
  description = "Map of metadata key/value pairs to make available within the instance"
  default     = {}
}

variable "metadata_startup_script" {
  type        = string
  description = "Startup script to be executed when the instance boots"
  default     = null
}

# Labels 
variable "labels" {
  type        = map(string)
  description = "Map of labels to be applied to the instance"
  default     = {}
}

# Tags
variable "tags" {
  type        = list(string)
  description = "List of tags to be attached to the instance"
  default     = []
}

variable "automatic_restart" {
  type        = bool
  description = "Specifies if the instance should be automatically restarted if it is terminated by Compute Engine"
  default     = true
}

variable "on_host_maintenance" {
  type        = string
  description = "Instance behavior on maintenance events. Options are MIGRATE or TERMINATE"
  default     = "MIGRATE"
}

variable "enable_secure_boot" {
  type        = bool
  description = "Verify the digital signature of all boot components. Requires shielded_vm to be true"
  default     = false
}

