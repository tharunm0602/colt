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
  project = "my-cloud-1"
  region  = "us-central1"
}

provider "google-beta" {
  project = "my-cloud-1"
  region  = "us-central1"
}

terraform {
  backend "gcs" {
    bucket = "build_logs_001"
    prefix = "gcs/sbx-colt-raw-data/state"
  }
}
