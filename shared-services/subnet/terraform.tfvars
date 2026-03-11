project_id   = "cloud-practice-dev-2"
region       = "us-central1"
network_name = "shared-vpc"
subnets = [
  {
    subnet_name           = "shared-subnet-01"
    subnet_ip             = "10.0.1.0/24"
    subnet_region         = "us-central1"
    subnet_private_access = "true"
  }
]
