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

# Pub/Sub Topic
resource "google_pubsub_topic" "topic" {
  name    = var.topic_name
  project = var.project_id
  labels  = var.labels

  dynamic "message_storage_policy" {
    for_each = var.message_storage_policy != null ? [var.message_storage_policy] : []
    content {
      allowed_persistence_regions = message_storage_policy.value.allowed_persistence_regions
    }
  }

  kms_key_name = var.kms_key_name
}

# Pub/Sub Subscriptions
resource "google_pubsub_subscription" "subscriptions" {
  for_each = var.subscriptions
  name     = each.key
  topic    = google_pubsub_topic.topic.name
  project  = var.project_id

  ack_deadline_seconds       = lookup(each.value, "ack_deadline_seconds", 10)
  message_retention_duration = lookup(each.value, "message_retention_duration", null)
  retain_acked_messages      = lookup(each.value, "retain_acked_messages", false)
  filter                     = lookup(each.value, "filter", null)
  enable_message_ordering    = lookup(each.value, "enable_message_ordering", false)

  dynamic "expiration_policy" {
    for_each = lookup(each.value, "expiration_policy", null) != null ? [each.value.expiration_policy] : []
    content {
      ttl = expiration_policy.value.ttl
    }
  }

  dynamic "retry_policy" {
    for_each = lookup(each.value, "retry_policy", null) != null ? [each.value.retry_policy] : []
    content {
      minimum_backoff = retry_policy.value.minimum_backoff
      maximum_backoff = retry_policy.value.maximum_backoff
    }
  }

  dynamic "dead_letter_policy" {
    for_each = lookup(each.value, "dead_letter_policy", null) != null ? [each.value.dead_letter_policy] : []
    content {
      dead_letter_topic     = dead_letter_policy.value.dead_letter_topic
      max_delivery_attempts = dead_letter_policy.value.max_delivery_attempts
    }
  }

  dynamic "push_config" {
    for_each = lookup(each.value, "push_config", null) != null ? [each.value.push_config] : []
    content {
      push_endpoint = push_config.value.push_endpoint
      attributes    = lookup(push_config.value, "attributes", null)

      dynamic "oidc_token" {
        for_each = lookup(push_config.value, "oidc_token", null) != null ? [push_config.value.oidc_token] : []
        content {
          service_account_email = oidc_token.value.service_account_email
          audience              = lookup(oidc_token.value, "audience", null)
        }
      }
    }
  }

  labels = var.labels
}
