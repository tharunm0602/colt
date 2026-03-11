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
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket = "build_logs_001"
    prefix = "shared-services/vpc/state"
  }
}
