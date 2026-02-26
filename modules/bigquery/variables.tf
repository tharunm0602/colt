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

# Core Configuration
variable "project_id" {
  type        = string
  description = "The project ID where BigQuery resources will be created"
}

variable "location" {
  type        = string
  description = "The location for BigQuery resources (e.g., US, EU, asia-northeast1)"
  default     = "us-central1"
}

variable "dataset_id" {
  type        = string
  description = "The ID of the BigQuery dataset"
}

variable "description" {
   description  = "Dataset description"
   type         = string
   default      = "Description for the dataset"
}

variable "delete_contents_on_destroy" {
    description = "Allow dataset deletion with contents"
    type        = bool
    default     = false
}

variable "labels" {
  type        = map(string)
  description = "Map of labels to be applied to BigQuery resources"
  default     = {}
}

variable "tables" {
    description = "Map of tables to create"
    type        = map(object({
        schema = string
        time_partitioning = optional(object({
            type                     = string
            field                    = optional(string)
            require_partition_filter = optional(bool)
        }))
        clustering = optional(list(string))
    }))
    default = {}
}

variable "table_deletion_protection" {
  type        = bool
  description = "Defines if the table should be protected against deletion"
  default     = true
}