/**
 * Cloud Monitoring module
 * - enables Monitoring API
 * - creates notification channels (email, slack, etc.)
 * - creates alert policies based on metrics
 * - optional uptime checks
 * - optional custom dashboards
 */

# Enable Monitoring API
resource "google_project_service" "monitoring_api" {
  project            = var.project_id
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}

# Alert Policy for High CPU
resource "google_monitoring_alert_policy" "cpu_alert" {
  project         = var.project_id
  display_name    = "High CPU  usage Alert"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "VM instance CPU utilization"

    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND metric.type=\"compute.googleapis.com/instance/cpu/utilization\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.cpu_threshold

      aggregations {
        alignment_period = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.notification_channels
  depends_on = [google_project_service.monitoring_api]
}