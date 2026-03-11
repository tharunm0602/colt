terraform {
  required_version = ">= 1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.19, < 8"
    }
  }

  backend "gcs" {
    bucket = "build_logs_001"
    prefix = "bootstrap/gcs/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
