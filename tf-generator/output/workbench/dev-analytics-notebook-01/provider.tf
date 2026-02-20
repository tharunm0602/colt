terraform {
  required_version = ">= 1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.19, < 8"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 6.19, < 8"
    }
  }
}

provider "google" {
  project = "test-dev-1"
  region  = "us-central1"
}

provider "google-beta" {
  project = "test-dev-1"
  region  = "us-central1"
}

terraform {
  backend "gcs" {
    bucket = "build_logs_001"
    prefix = "workbench/dev-analytics-notebook-01/state"
  }
}
