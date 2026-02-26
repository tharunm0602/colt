/**
 * Cloud Logging module
 * - enables Logging API
 * - optional creation of Storage bucket, BigQuery dataset, PubSub topic
 * - creates a project-level log sink and grants writer identity necessary permissions
 */

# Enable Logging API
resource "google_project_service" "logging_api" {
  project            = var.project_id
  service            = "logging.googleapis.com"
  disable_on_destroy = false
}

# Logging sink
resource "google_logging_project_sink" "log_sink" {
  project         = var.project_id
  name            = var.sink_name
  destination     = var.destination
  filter          = var.log_filter

  unique_writer_identity = true

  depends_on = [google_project_service.logging_api]
}