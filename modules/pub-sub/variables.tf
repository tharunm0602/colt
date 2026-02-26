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

variable "project_id" {
  type        = string
  description = "The project ID where Pub/Sub resources will be created"
}

variable "topic_name" {
  type        = string
  description = "The name of the Pub/Sub topic"
}

variable "labels" {
  type        = map(string)
  description = "Map of labels to be applied to Pub/Sub resources"
  default     = {}
}

variable "kms_key_name" {
  type        = string
  description = "The resource name of the Cloud KMS CryptoKey to be used to protect messages published on this topic"
  default     = null
}

variable "message_storage_policy" {
  type = object({
    allowed_persistence_regions = list(string)
  })
  description = "Policy constraining the localities of storage of messages at rest"
  default     = null
}

variable "subscriptions" {
  type        = any
  description = "Map of subscriptions to create for the topic"
  default     = {}
}
