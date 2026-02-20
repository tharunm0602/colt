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

# Cloud SQL Instance
resource "google_sql_database_instance" "instance" {
  name                = var.instance_name
  database_version    = var.database_version
  region              = var.region
  project             = var.project_id

  deletion_protection = var.deletion_protection

  settings {
    tier              = var.instance_tier
    availability_type = var.availability_type
    disk_type         = var.disk_type
    disk_size         = var.disk_size_gb
    disk_autoresize   = true

    # Backup Configuration
    backup_configuration" {
        enabled                        = var.backup_enabled
        start_time                     = var.backup_start_time
        point_in_time_recovery_enabled = var.point_in_time_recovery_enabled
    }

    # IP Configuration
    ip_configuration" {
        ipv4_enabled    = var.enable_public_ip
        private_network = var.private_network
        require_ssl     = var.require_ssl
    }

    # Maintenance Window
    maintenance_window" {
        day          = var.maintenance_day
        hour         = var.maintenance_hour
      }

    # Database Flags
    dynamic "database_flags" {
      for_each = var.database_flags

      content {
        name  = database_flags.value.name
        value = database_flags.value.value
      }
    }

    user_labels = var.labels
    }
}

# Cloud SQL Database
resource "google_sql_database" "default_database" {
  count     = var.create_default_database ? 1 : 0
  name      = var.default_database_name
  instance  = google_sql_database_instance.instance.name
  project   = var.project_id
}

# Cloud SQL User
resource "google_sql_user" "default_user" {
  count    = var.create_default_user ? 1 : 0
  name     = var.default_user_name
  instance = google_sql_database_instance.instance.name
  password = var.default_user_password
  project  = var.project_id
}