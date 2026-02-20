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

# Compute Instance Resource
resource "google_compute_instance" "instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone
  project      = var.project_id


  # Boot disk configuration
  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size  = var.boot_disk_size
      type  = var.boot_disk_type
    }
  }

  # Network interface configuration
  network_interface {
    network    = var.network
    subnetwork = var.subnetwork

    # Public IP configuration
    dynamic "access_config" {
      for_each = var.enable_public_ip ? [1] : []
      content {}
    }
  }

  # Service Account
  service_account {
    email  = var.service_account_email
    scopes = var.service_account_scopes
  }

  # Metadata
  metadata = var.metadata
  metadata_startup_script = var.metadata_startup_script

  # Labels
  labels = var.labels

  #Tags
  tags = var.network_tags

  scheduling {
    automatic_restart = var.automatic_restart
    on_host_maintenance = var.on_host_maintenance
  }

  shielded_instance_config {
    enable_secure_boot          = var.enable_secure_boot
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
}
