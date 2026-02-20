"""
Terraform Template Generator Module.
Generates Terraform files based on the module templates in the repository.
Improved: Added subnet generation and better error handling.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from config import DEFAULTS, DEFAULT_REGION, BACKEND_BUCKET, TERRAFORM_VERSION, GOOGLE_PROVIDER_VERSION
from parser import InfrastructureSpec


@dataclass
class GeneratedFiles:
    """Container for generated Terraform file contents."""
    main_tf: str
    variables_tf: str
    terraform_tfvars: str
    provider_tf: str


class TerraformGenerator:
    """Generates Terraform files based on module templates."""
    
    def __init__(self, project_id: str, region: str = DEFAULT_REGION):
        """
        Initialize the generator.
        
        Args:
            project_id: GCP project ID
            region: GCP region (default: us-central1)
        """
        self.project_id = project_id
        self.region = region
    
    def generate_provider_tf(self, resource_type: str, resource_name: str) -> str:
        """Generate provider.tf content."""
        return f'''terraform {{
  required_version = "{TERRAFORM_VERSION}"

  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "{GOOGLE_PROVIDER_VERSION}"
    }}
    google-beta = {{
      source  = "hashicorp/google-beta"
      version = "{GOOGLE_PROVIDER_VERSION}"
    }}
  }}
}}

provider "google" {{
  project = "{self.project_id}"
  region  = "{self.region}"
}}

provider "google-beta" {{
  project = "{self.project_id}"
  region  = "{self.region}"
}}

terraform {{
  backend "gcs" {{
    bucket = "{BACKEND_BUCKET}"
    prefix = "{resource_type}/{resource_name}/state"
  }}
}}
'''
    
    def generate_vpc(self, vpc_name: str) -> GeneratedFiles:
        """Generate VPC Terraform files."""
        defaults = DEFAULTS["vpc"]
        
        main_tf = f'''module "vpc" {{
  source = "../../../../modules/vpc/"

  project_id                   = var.project_id
  network_name                 = var.vpc_name
  mtu                          = var.mtu
  routing_mode                 = "{defaults['routing_mode']}"
  enable_ipv6_ula              = {str(defaults['enable_ipv6_ula']).lower()}
  shared_vpc_host              = {str(defaults['shared_vpc_host']).lower()}
  bgp_best_path_selection_mode = "{defaults['bgp_best_path_selection_mode']}"
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID where the VPC will be created"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "mtu" {
  description = "MTU size for the VPC network"
  type        = number
  default     = 1460
}
'''
        
        terraform_tfvars = f'''project_id = "{self.project_id}"
vpc_name   = "{vpc_name}"
mtu        = {defaults['mtu']}
'''
        
        provider_tf = self.generate_provider_tf("vpc", vpc_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )
    
    def generate_subnet(self, subnet_name: str, vpc_name: str, cidr: str) -> GeneratedFiles:
        """Generate Subnet Terraform files."""
        defaults = DEFAULTS["subnet"]
        
        main_tf = f'''module "subnet" {{
  source = "../../../../modules/subnet/"

  project_id   = var.project_id
  network_name = var.network_name

  subnets = [
    {{
      subnet_name           = var.subnet_name
      subnet_ip             = var.subnet_cidr
      subnet_region         = var.region
      subnet_private_access = "{str(defaults['private_ip_google_access']).lower()}"
      subnet_flow_logs      = "{str(defaults['enable_flow_logs']).lower()}"
      description           = "Managed by Terraform"
    }}
  ]
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
}

variable "subnet_cidr" {
  description = "IP CIDR range for the subnet"
  type        = string
}

variable "region" {
  description = "Region for the subnet"
  type        = string
}
'''
        
        terraform_tfvars = f'''project_id   = "{self.project_id}"
network_name = "{vpc_name}"
subnet_name  = "{subnet_name}"
subnet_cidr  = "{cidr}"
region       = "{self.region}"
'''
        
        provider_tf = self.generate_provider_tf("subnet", subnet_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )
    
    def generate_service_account(self, sa_name: str, roles: List[str]) -> GeneratedFiles:
        """Generate Service Account Terraform files."""
        defaults = DEFAULTS["service_account"]
        
        # Format roles list
        roles_str = ",\n    ".join([f'"{role}"' for role in roles])
        
        main_tf = f'''module "service_account" {{
  source = "../../../../modules/service-account"

  project_id    = var.project_id
  name          = var.sa_name
  display_name  = var.display_name

  project_roles = [
    {roles_str}
  ]
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "sa_name" {
  description = "Service Account name"
  type        = string
}

variable "display_name" {
  description = "Service Account display name"
  type        = string
}
'''
        
        # Create display name from SA name
        display_name = sa_name.replace("-", " ").title() + " Service Account"
        
        terraform_tfvars = f'''project_id   = "{self.project_id}"
sa_name      = "{sa_name}"
display_name = "{display_name}"
'''
        
        provider_tf = self.generate_provider_tf("sa", sa_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )
    
    def generate_gcs_bucket(self, bucket_name: str) -> GeneratedFiles:
        """Generate GCS Bucket Terraform files."""
        defaults = DEFAULTS["gcs"]
        
        main_tf = f'''module "gcs_bucket" {{
  source = "../../../../modules/gcs"

  project_id    = var.project_id
  name          = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
  versioning    = {str(defaults['versioning']).lower()}
  force_destroy = {str(defaults['force_destroy']).lower()}
  bucket_policy_only = {str(defaults['bucket_policy_only']).lower()}

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "bucket_name" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "location" {
  description = "Location for the bucket"
  type        = string
}

variable "storage_class" {
  description = "Storage class for the bucket"
  type        = string
  default     = "STANDARD"
}
'''
        
        terraform_tfvars = f'''project_id    = "{self.project_id}"
bucket_name   = "{bucket_name}"
location      = "{self.region.upper()}"
storage_class = "{defaults['storage_class']}"
'''
        
        provider_tf = self.generate_provider_tf("gcs", bucket_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )
    
    def generate_artifact_registry(self, repo_name: str) -> GeneratedFiles:
        """Generate Artifact Registry Terraform files."""
        defaults = DEFAULTS["artifact_registry"]
        
        main_tf = f'''module "artifact_registry" {{
  source = "../../../../modules/artifact-registry"

  project_id    = var.project_id
  repository_id = var.repository_id
  location      = var.location
  format        = var.format
  description   = var.description
  mode          = "{defaults['mode']}"

  docker_config = {{
    immutable_tags = {str(defaults['docker_config']['immutable_tags']).lower()}
  }}

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "repository_id" {
  description = "Repository name"
  type        = string
}

variable "location" {
  description = "Location for the repository"
  type        = string
}

variable "format" {
  description = "Repository format (DOCKER, MAVEN, NPM, PYTHON)"
  type        = string
  default     = "DOCKER"
}

variable "description" {
  description = "Repository description"
  type        = string
  default     = "Artifact Registry Repository"
}
'''
        
        terraform_tfvars = f'''project_id    = "{self.project_id}"
repository_id = "{repo_name}"
location      = "{self.region}"
format        = "{defaults['format']}"
description   = "{defaults['description']}"
'''
        
        provider_tf = self.generate_provider_tf("artifact-registry", repo_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )
    
    def generate_workbench(self, instance_name: str, network: str, subnet: str) -> GeneratedFiles:
        """Generate Workbench Terraform files."""
        defaults = DEFAULTS["workbench"]
        
        main_tf = f'''module "workbench" {{
  source = "../../../../modules/workbench"

  project_id        = var.project_id
  name              = var.instance_name
  location          = var.location
  machine_type      = var.machine_type
  boot_disk_size_gb = var.boot_disk_size_gb
  boot_disk_type    = var.boot_disk_type
  disable_public_ip = {str(defaults['disable_public_ip']).lower()}
  disk_encryption   = "{defaults['disk_encryption']}"

  network_interfaces = [{{
    network  = var.network
    subnet   = var.subnet
    nic_type = "VIRTIO_NET"
  }}]

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}
}}
'''
        
        variables_tf = '''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "instance_name" {
  description = "Workbench instance name"
  type        = string
}

variable "location" {
  description = "Zone for the instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type"
  type        = string
  default     = "e2-medium"
}

variable "network" {
  description = "VPC network name"
  type        = string
}

variable "subnet" {
  description = "Subnet name"
  type        = string
}

variable "boot_disk_size_gb" {
  description = "Boot disk size in GB"
  type        = number
  default     = 150
}

variable "boot_disk_type" {
  description = "Boot disk type"
  type        = string
  default     = "PD_BALANCED"
}
'''
        
        terraform_tfvars = f'''project_id        = "{self.project_id}"
instance_name     = "{instance_name}"
location          = "{self.region}-a"
machine_type      = "{defaults['machine_type']}"
network           = "{network}"
subnet            = "{subnet}"
boot_disk_size_gb = {defaults['boot_disk_size_gb']}
boot_disk_type    = "{defaults['boot_disk_type']}"
'''
        
        provider_tf = self.generate_provider_tf("workbench", instance_name)
        
        return GeneratedFiles(
            main_tf=main_tf,
            variables_tf=variables_tf,
            terraform_tfvars=terraform_tfvars,
            provider_tf=provider_tf
        )


def generate_all(spec: InfrastructureSpec, project_id: str, region: str = DEFAULT_REGION) -> Dict[str, GeneratedFiles]:
    """
    Generate all Terraform files based on the infrastructure specification.
    
    Args:
        spec: Infrastructure specification from parsed document
        project_id: GCP project ID
        region: GCP region
        
    Returns:
        Dictionary mapping resource names to their generated files
    """
    generator = TerraformGenerator(project_id, region)
    generated = {}
    
    # Generate VPC
    if spec.vpc_name:
        generated[f"vpc/{spec.vpc_name}"] = generator.generate_vpc(spec.vpc_name)
    
    # Generate Subnet (requires VPC)
    if spec.subnet_cidr and spec.vpc_name:
        subnet_name = spec.subnet_name or f"{spec.vpc_name}-subnet-01"
        generated[f"subnet/{subnet_name}"] = generator.generate_subnet(
            subnet_name,
            spec.vpc_name,
            spec.subnet_cidr
        )
    
    # Generate Service Account
    if spec.service_account_name:
        # Extract just the account ID from the full name
        sa_name = spec.service_account_name.split("@")[0] if "@" in spec.service_account_name else spec.service_account_name
        
        # Use extracted roles or default to viewer
        roles = spec.service_account_roles if spec.service_account_roles else ["roles/viewer"]
        
        generated[f"sa/{sa_name}"] = generator.generate_service_account(sa_name, roles)
    
    # Generate GCS Buckets
    for bucket_name in spec.bucket_names:
        generated[f"gcs/{bucket_name}"] = generator.generate_gcs_bucket(bucket_name)
    
    # Generate Artifact Registry
    if spec.artifact_registry_name:
        generated[f"artifact-registry/{spec.artifact_registry_name}"] = generator.generate_artifact_registry(
            spec.artifact_registry_name
        )
    
    # Generate Workbench (requires VPC and Subnet)
    if spec.workbench_name:
        network = spec.workbench_network or spec.vpc_name
        
        # Use the generated subnet name, not "default"
        if spec.subnet_name:
            subnet = spec.subnet_name
        elif spec.vpc_name:
            subnet = f"{spec.vpc_name}-subnet-01"
        else:
            subnet = "default"  # Fallback only if no VPC
        
        if network:  # Only generate if we have a network
            generated[f"workbench/{spec.workbench_name}"] = generator.generate_workbench(
                spec.workbench_name,
                network,
                subnet
            )
    
    return generated


@dataclass
class SingleFileOutput:
    """Container for single-file generation output."""
    main_tf: str
    variables_tf: str
    terraform_tfvars: str
    provider_tf: str
    outputs_tf: str


def generate_single_file(spec: InfrastructureSpec, project_id: str, region: str = DEFAULT_REGION) -> SingleFileOutput:
    """
    Generate all Terraform resources in a single set of files.
    
    Args:
        spec: Infrastructure specification from parsed document
        project_id: GCP project ID
        region: GCP region
        
    Returns:
        SingleFileOutput with all resources combined
    """
    defaults = DEFAULTS
    
    # Build main.tf with all modules
    main_tf_parts = []
    variables_tf_parts = []
    tfvars_parts = []
    outputs_tf_parts = []
    
    # Common variables
    variables_tf_parts.append('''variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}
''')
    
    tfvars_parts.append(f'''project_id = "{project_id}"
region     = "{region}"
''')
    
    # VPC
    if spec.vpc_name:
        main_tf_parts.append(f'''
# =============================================================================
# VPC Network
# =============================================================================
module "vpc" {{
  source = "../../../modules/vpc/"

  project_id                   = var.project_id
  network_name                 = var.vpc_name
  mtu                          = var.mtu
  routing_mode                 = "{defaults['vpc']['routing_mode']}"
  enable_ipv6_ula              = {str(defaults['vpc']['enable_ipv6_ula']).lower()}
  shared_vpc_host              = {str(defaults['vpc']['shared_vpc_host']).lower()}
  bgp_best_path_selection_mode = "{defaults['vpc']['bgp_best_path_selection_mode']}"
}}
''')
        variables_tf_parts.append('''
variable "vpc_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "mtu" {
  description = "MTU size for the VPC network"
  type        = number
  default     = 1460
}
''')
        tfvars_parts.append(f'''
# VPC
vpc_name = "{spec.vpc_name}"
mtu      = {defaults['vpc']['mtu']}
''')
        outputs_tf_parts.append('''
output "vpc_name" {
  value = module.vpc.network_name
}
''')
    
    # Subnet
    if spec.subnet_cidr and spec.vpc_name:
        subnet_name = spec.subnet_name or f"{spec.vpc_name}-subnet-01"
        main_tf_parts.append(f'''
# =============================================================================
# Subnet
# =============================================================================
module "subnet" {{
  source = "../../../modules/subnet/"

  project_id   = var.project_id
  network_name = module.vpc.network_name

  subnets = [
    {{
      subnet_name           = var.subnet_name
      subnet_ip             = var.subnet_cidr
      subnet_region         = var.region
      subnet_private_access = "{str(defaults['subnet']['private_ip_google_access']).lower()}"
      subnet_flow_logs      = "{str(defaults['subnet']['enable_flow_logs']).lower()}"
      description           = "Managed by Terraform"
    }}
  ]

  depends_on = [module.vpc]
}}
''')
        variables_tf_parts.append('''
variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
}

variable "subnet_cidr" {
  description = "IP CIDR range for the subnet"
  type        = string
}
''')
        tfvars_parts.append(f'''
# Subnet
subnet_name = "{subnet_name}"
subnet_cidr = "{spec.subnet_cidr}"
''')
    
    # Service Account
    if spec.service_account_name:
        sa_name = spec.service_account_name.split("@")[0] if "@" in spec.service_account_name else spec.service_account_name
        roles = spec.service_account_roles if spec.service_account_roles else ["roles/viewer"]
        roles_str = ",\n    ".join([f'"{role}"' for role in roles])
        
        main_tf_parts.append(f'''
# =============================================================================
# Service Account
# =============================================================================
module "service_account" {{
  source = "../../../modules/service-account"

  project_id    = var.project_id
  name          = var.sa_name
  display_name  = var.sa_display_name

  project_roles = [
    {roles_str}
  ]
}}
''')
        variables_tf_parts.append('''
variable "sa_name" {
  description = "Service Account name"
  type        = string
}

variable "sa_display_name" {
  description = "Service Account display name"
  type        = string
}
''')
        display_name = sa_name.replace("-", " ").title() + " Service Account"
        tfvars_parts.append(f'''
# Service Account
sa_name         = "{sa_name}"
sa_display_name = "{display_name}"
''')
        outputs_tf_parts.append('''
output "service_account_email" {
  value = module.service_account.email
}
''')
    
    # GCS Buckets
    for i, bucket_name in enumerate(spec.bucket_names):
        bucket_var = f"bucket_{i+1}_name"
        main_tf_parts.append(f'''
# =============================================================================
# GCS Bucket: {bucket_name}
# =============================================================================
module "gcs_bucket_{i+1}" {{
  source = "../../../modules/gcs"

  project_id         = var.project_id
  name               = var.{bucket_var}
  location           = upper(var.region)
  storage_class      = "{defaults['gcs']['storage_class']}"
  versioning         = {str(defaults['gcs']['versioning']).lower()}
  force_destroy      = {str(defaults['gcs']['force_destroy']).lower()}
  bucket_policy_only = {str(defaults['gcs']['bucket_policy_only']).lower()}

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}
}}
''')
        variables_tf_parts.append(f'''
variable "{bucket_var}" {{
  description = "Name of GCS bucket {i+1}"
  type        = string
}}
''')
        tfvars_parts.append(f'''
# GCS Bucket {i+1}
{bucket_var} = "{bucket_name}"
''')
    
    # Artifact Registry
    if spec.artifact_registry_name:
        main_tf_parts.append(f'''
# =============================================================================
# Artifact Registry
# =============================================================================
module "artifact_registry" {{
  source = "../../../modules/artifact-registry"

  project_id    = var.project_id
  repository_id = var.artifact_registry_name
  location      = var.region
  format        = "{defaults['artifact_registry']['format']}"
  description   = "{defaults['artifact_registry']['description']}"
  mode          = "{defaults['artifact_registry']['mode']}"

  docker_config = {{
    immutable_tags = {str(defaults['artifact_registry']['docker_config']['immutable_tags']).lower()}
  }}

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}
}}
''')
        variables_tf_parts.append('''
variable "artifact_registry_name" {
  description = "Artifact Registry repository name"
  type        = string
}
''')
        tfvars_parts.append(f'''
# Artifact Registry
artifact_registry_name = "{spec.artifact_registry_name}"
''')
    
    # Workbench
    if spec.workbench_name and spec.vpc_name:
        main_tf_parts.append(f'''
# =============================================================================
# Workbench Instance
# =============================================================================
module "workbench" {{
  source = "../../../modules/workbench"

  project_id        = var.project_id
  name              = var.workbench_name
  location          = "${{var.region}}-a"
  machine_type      = "{defaults['workbench']['machine_type']}"
  boot_disk_size_gb = {defaults['workbench']['boot_disk_size_gb']}
  boot_disk_type    = "{defaults['workbench']['boot_disk_type']}"
  disable_public_ip = {str(defaults['workbench']['disable_public_ip']).lower()}
  disk_encryption   = "{defaults['workbench']['disk_encryption']}"

  network_interfaces = [{{
    network  = module.vpc.network_name
    subnet   = var.subnet_name
    nic_type = "VIRTIO_NET"
  }}]

  labels = {{
    environment = "sbx"
    managed_by  = "terraform"
  }}

  depends_on = [module.subnet]
}}
''')
        variables_tf_parts.append('''
variable "workbench_name" {
  description = "Workbench instance name"
  type        = string
}
''')
        tfvars_parts.append(f'''
# Workbench
workbench_name = "{spec.workbench_name}"
''')
    
    # Provider
    provider_tf = f'''terraform {{
  required_version = "{TERRAFORM_VERSION}"

  required_providers {{
    google = {{
      source  = "hashicorp/google"
      version = "{GOOGLE_PROVIDER_VERSION}"
    }}
    google-beta = {{
      source  = "hashicorp/google-beta"
      version = "{GOOGLE_PROVIDER_VERSION}"
    }}
  }}
}}

provider "google" {{
  project = var.project_id
  region  = var.region
}}

provider "google-beta" {{
  project = var.project_id
  region  = var.region
}}

terraform {{
  backend "gcs" {{
    bucket = "{BACKEND_BUCKET}"
    prefix = "infrastructure/state"
  }}
}}
'''
    
    return SingleFileOutput(
        main_tf="".join(main_tf_parts),
        variables_tf="".join(variables_tf_parts),
        terraform_tfvars="".join(tfvars_parts),
        provider_tf=provider_tf,
        outputs_tf="".join(outputs_tf_parts) if outputs_tf_parts else "# No outputs defined\n"
    )

