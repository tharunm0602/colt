provider "google" {
  credentials = file("../${var.project}-${var.envname}.json")
  project     = "${var.project}-${var.envname}"
  region      = var.region # Choose the appropriate region for your bucket
}

provider "google-beta" {
  credentials = file("../${var.project}-${var.envname}.json")
  project     = "${var.project}-${var.envname}"
  region      = var.region # Choose the appropriate region for your bucket
}
