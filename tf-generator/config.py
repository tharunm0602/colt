"""
Configuration and default values for the Terraform Generator.
Improved: Configurable naming patterns instead of hardcoded values.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


# =============================================================================
# NAMING PATTERNS - Configurable patterns for resource extraction
# =============================================================================
# These patterns are used to identify resources in documents.
# Modify these to match your organization's naming conventions.

@dataclass
class NamingPatterns:
    """Configurable naming patterns for resource extraction."""
    
    # Prefix used in your organization (e.g., "sbx-colt", "prod-acme", "dev-myorg")
    org_prefix: str = "sbx-colt"
    
    # VPC patterns - will be combined with org_prefix
    vpc_suffixes: List[str] = field(default_factory=lambda: ["vpc", "network", "net"])
    
    # Service Account patterns
    sa_suffixes: List[str] = field(default_factory=lambda: ["sa", "svc", "service"])
    
    # Bucket patterns - keywords that indicate a bucket
    bucket_keywords: List[str] = field(default_factory=lambda: ["data", "bucket", "storage", "lake", "archive"])
    
    # Workbench patterns
    workbench_keywords: List[str] = field(default_factory=lambda: ["workbench", "notebook", "jupyter", "vertex"])
    
    # Artifact Registry patterns
    artifact_keywords: List[str] = field(default_factory=lambda: ["artifact", "registry", "docker", "container", "repo"])
    
    def get_vpc_patterns(self) -> List[str]:
        """Generate VPC regex patterns."""
        patterns = []
        # Pattern with org prefix
        for suffix in self.vpc_suffixes:
            patterns.append(rf"{self.org_prefix}-[a-zA-Z0-9-]*{suffix}[a-zA-Z0-9-]*")
            patterns.append(rf"{self.org_prefix}-{suffix}[a-zA-Z0-9-]*")
        # Generic VPC patterns (fallback)
        patterns.append(r"[a-zA-Z0-9-]+-vpc[a-zA-Z0-9-]*")
        patterns.append(r"VPC[\s:]+([a-zA-Z0-9-_]+)")
        return patterns
    
    def get_sa_patterns(self) -> List[str]:
        """Generate Service Account regex patterns."""
        patterns = []
        # Pattern with org prefix and PROJECT_ID placeholder
        patterns.append(rf"({self.org_prefix}-[a-zA-Z0-9-]*)<<PROJECT_ID>>@")
        patterns.append(rf"({self.org_prefix}-[a-zA-Z0-9-]*)@[a-zA-Z0-9-]+\.iam")
        # Named patterns
        patterns.append(r"Service Account[:\s|]+([a-zA-Z0-9-_@.]+)")
        # Generic SA patterns
        for suffix in self.sa_suffixes:
            patterns.append(rf"([a-zA-Z0-9-]+-{suffix}[a-zA-Z0-9-]*)@")
        return patterns
    
    def get_bucket_patterns(self) -> List[str]:
        """Generate GCS bucket regex patterns."""
        patterns = []
        # Pattern with org prefix
        for keyword in self.bucket_keywords:
            patterns.append(rf"{self.org_prefix}-[a-zA-Z0-9-]*{keyword}[a-zA-Z0-9-]*")
            patterns.append(rf"{self.org_prefix}-{keyword}[a-zA-Z0-9-]*")
        # Named patterns
        patterns.append(r"Bucket[\s:]+([a-zA-Z0-9-_]+)")
        patterns.append(r"GCS[\s:]+([a-zA-Z0-9-_]+)")
        return patterns
    
    def get_workbench_patterns(self) -> List[str]:
        """Generate Workbench regex patterns."""
        patterns = []
        for keyword in self.workbench_keywords:
            patterns.append(rf"{self.org_prefix}-[a-zA-Z0-9-]*{keyword}[a-zA-Z0-9-]*")
        patterns.append(r"Workbench[\s:]+([a-zA-Z0-9-_]+)")
        patterns.append(r"Notebook[\s:]+([a-zA-Z0-9-_]+)")
        return patterns
    
    def get_artifact_patterns(self) -> List[str]:
        """Generate Artifact Registry regex patterns."""
        patterns = []
        for keyword in self.artifact_keywords:
            patterns.append(rf"{self.org_prefix}-[a-zA-Z0-9-]*{keyword}[a-zA-Z0-9-]*")
        patterns.append(r"Repository[\s:]+([a-zA-Z0-9-_]+)")
        patterns.append(r"Artifact Registry[\s:]+([a-zA-Z0-9-_]+)")
        return patterns


# Default naming patterns - can be overridden
NAMING_PATTERNS = NamingPatterns()


# =============================================================================
# GCP DEFAULTS
# =============================================================================

# Default region for GCP resources
DEFAULT_REGION = "us-central1"

# Default values for optional fields
DEFAULTS = {
    "artifact_registry": {
        "format": "DOCKER",
        "mode": "STANDARD_REPOSITORY",
        "description": "Artifact Registry Repository",
        "docker_config": {
            "immutable_tags": True
        }
    },
    "gcs": {
        "storage_class": "STANDARD",
        "versioning": True,
        "force_destroy": False,
        "bucket_policy_only": True
    },
    "vpc": {
        "routing_mode": "REGIONAL",
        "mtu": 1460,
        "shared_vpc_host": False,
        "enable_ipv6_ula": False,
        "bgp_best_path_selection_mode": "STANDARD"
    },
    "subnet": {
        "private_ip_google_access": True,
        "enable_flow_logs": False,
        "purpose": "PRIVATE"
    },
    "service_account": {
        "display_name": "Terraform-managed service account",
        "description": ""
    },
    "workbench": {
        "machine_type": "e2-medium",
        "boot_disk_size_gb": 150,
        "boot_disk_type": "PD_BALANCED",
        "disable_public_ip": True,
        "disk_encryption": "GMEK"
    }
}


# =============================================================================
# TERRAFORM BACKEND
# =============================================================================

# Terraform backend configuration
BACKEND_BUCKET = "build_logs_001"

# Provider versions
TERRAFORM_VERSION = ">= 1.3"
GOOGLE_PROVIDER_VERSION = ">= 6.19, < 8"


# =============================================================================
# ROLE PATTERNS - For extracting IAM roles
# =============================================================================

# Pattern to match GCP IAM roles
ROLE_PATTERN = r"roles/([a-zA-Z0-9._]+)"


# =============================================================================
# VALIDATION RULES
# =============================================================================

# Minimum required resources for a valid deployment
REQUIRED_RESOURCES = {
    "must_have_one": ["vpc", "gcs", "service_account"],  # At least one of these
    "dependencies": {
        "workbench": ["vpc"],  # Workbench requires VPC
        "subnet": ["vpc"],     # Subnet requires VPC
    }
}
