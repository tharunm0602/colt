###########################################
### Static Layer Remote TF State file   ###
###########################################

data "terraform_remote_state" "static" {
  backend = "gcs"
  config = {
    bucket = "aicoe-${var.envname}-bucket-tf-state"
    prefix = "tf-static"
  }
}
