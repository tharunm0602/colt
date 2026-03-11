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

  backend "gcs" {
    bucket = "build_logs_001"
    prefix = "bootstrap/project/state"
  }
}

provider "google" {
  region  = var.region
}

provider "google-beta" {
  region  = var.region
}
