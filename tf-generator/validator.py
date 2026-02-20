"""
Validator Module - Validates existing Terraform files against document specifications.
Fixed: Now correctly handles nested directory structure (output/type/name/)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from parser import InfrastructureSpec


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    resource_type: str
    resource_name: str
    issues: List[str]
    matches: List[str]


class TerraformValidator:
    """Validates existing Terraform files against infrastructure specifications."""
    
    def __init__(self, output_dir: str):
        """
        Initialize validator.
        
        Args:
            output_dir: Directory containing generated Terraform files
        """
        self.output_dir = Path(output_dir)
    
    def check_existing_files(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Check for existing Terraform files in the output directory.
        Fixed: Now handles nested structure (output/type/name/)
        
        Returns:
            Dictionary mapping resource types to their subdirectories and files
            Example: {"vpc": {"sbx-colt-vpc": ["main.tf", "variables.tf", ...]}}
        """
        existing = {}
        
        if not self.output_dir.exists():
            return existing
        
        # First level: resource types (vpc, sa, gcs, etc.)
        for resource_type_dir in self.output_dir.iterdir():
            if resource_type_dir.is_dir():
                resource_type = resource_type_dir.name
                existing[resource_type] = {}
                
                # Second level: resource names (sbx-colt-vpc, sbx-colt-sa, etc.)
                for resource_name_dir in resource_type_dir.iterdir():
                    if resource_name_dir.is_dir():
                        tf_files = list(resource_name_dir.glob("*.tf")) + list(resource_name_dir.glob("*.tfvars"))
                        if tf_files:
                            existing[resource_type][resource_name_dir.name] = [f.name for f in tf_files]
        
        return existing
    
    def validate_against_spec(self, spec: InfrastructureSpec) -> List[ValidationResult]:
        """
        Validate existing files against the infrastructure specification.
        
        Args:
            spec: Infrastructure specification from parsed document
            
        Returns:
            List of validation results
        """
        results = []
        existing = self.check_existing_files()
        
        # Check VPC
        if spec.vpc_name:
            vpc_result = self._validate_vpc(spec.vpc_name, existing)
            results.append(vpc_result)
        
        # Check Subnet (if we have CIDR)
        if spec.subnet_cidr and spec.vpc_name:
            subnet_result = self._validate_subnet(spec.vpc_name, spec.subnet_cidr, existing)
            results.append(subnet_result)
        
        # Check Service Account
        if spec.service_account_name:
            sa_result = self._validate_service_account(spec.service_account_name, existing)
            results.append(sa_result)
        
        # Check Buckets
        for bucket_name in spec.bucket_names:
            bucket_result = self._validate_bucket(bucket_name, existing)
            results.append(bucket_result)
        
        # Check Artifact Registry
        if spec.artifact_registry_name:
            ar_result = self._validate_artifact_registry(spec.artifact_registry_name, existing)
            results.append(ar_result)
        
        # Check Workbench
        if spec.workbench_name:
            wb_result = self._validate_workbench(spec.workbench_name, existing)
            results.append(wb_result)
        
        return results
    
    def _validate_vpc(self, vpc_name: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate VPC configuration."""
        issues = []
        matches = []
        
        # Look for vpc in resource types
        if "vpc" not in existing:
            issues.append("No VPC configuration found")
            return ValidationResult(False, "vpc", vpc_name, issues, matches)
        
        vpc_resources = existing["vpc"]
        
        # Check if the specific VPC exists
        if vpc_name in vpc_resources:
            # Verify tfvars content
            tfvars_path = self.output_dir / "vpc" / vpc_name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if vpc_name in content:
                    matches.append(f"VPC '{vpc_name}' configuration found and matches")
                else:
                    issues.append(f"VPC tfvars exists but name mismatch")
            else:
                issues.append(f"VPC directory exists but no terraform.tfvars")
        else:
            # Check if any VPC exists with different name
            if vpc_resources:
                issues.append(f"VPC directory exists but for different VPC: {list(vpc_resources.keys())}")
            else:
                issues.append("No VPC configuration found")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "vpc", vpc_name, issues, matches)
    
    def _validate_subnet(self, vpc_name: str, cidr: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate Subnet configuration."""
        issues = []
        matches = []
        
        subnet_name = f"{vpc_name}-subnet"
        
        if "subnet" not in existing:
            issues.append(f"No Subnet configuration found (expected for CIDR {cidr})")
            return ValidationResult(False, "subnet", subnet_name, issues, matches)
        
        subnet_resources = existing["subnet"]
        
        # Check if subnet for this VPC exists
        found = False
        for name, files in subnet_resources.items():
            tfvars_path = self.output_dir / "subnet" / name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if cidr in content:
                    matches.append(f"Subnet with CIDR '{cidr}' found in {name}")
                    found = True
                    break
        
        if not found:
            issues.append(f"No subnet found with CIDR {cidr}")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "subnet", subnet_name, issues, matches)
    
    def _validate_service_account(self, sa_name: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate Service Account configuration."""
        issues = []
        matches = []
        
        if "sa" not in existing:
            issues.append("No Service Account configuration found")
            return ValidationResult(False, "service_account", sa_name, issues, matches)
        
        sa_resources = existing["sa"]
        
        # Check if the specific SA exists
        if sa_name in sa_resources:
            tfvars_path = self.output_dir / "sa" / sa_name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if sa_name in content:
                    matches.append(f"Service Account '{sa_name}' configuration found and matches")
                else:
                    issues.append(f"SA tfvars exists but name mismatch")
        else:
            if sa_resources:
                issues.append(f"SA directory exists but for different SA: {list(sa_resources.keys())}")
            else:
                issues.append("No Service Account configuration found")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "service_account", sa_name, issues, matches)
    
    def _validate_bucket(self, bucket_name: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate GCS Bucket configuration."""
        issues = []
        matches = []
        
        if "gcs" not in existing:
            issues.append(f"No GCS configuration found for {bucket_name}")
            return ValidationResult(False, "gcs", bucket_name, issues, matches)
        
        gcs_resources = existing["gcs"]
        
        if bucket_name in gcs_resources:
            tfvars_path = self.output_dir / "gcs" / bucket_name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if bucket_name in content:
                    matches.append(f"Bucket '{bucket_name}' configuration found and matches")
                else:
                    issues.append(f"Bucket tfvars exists but name mismatch")
        else:
            issues.append(f"Bucket '{bucket_name}' not found in existing configurations")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "gcs", bucket_name, issues, matches)
    
    def _validate_artifact_registry(self, repo_name: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate Artifact Registry configuration."""
        issues = []
        matches = []
        
        if "artifact-registry" not in existing:
            issues.append("No Artifact Registry configuration found")
            return ValidationResult(False, "artifact_registry", repo_name, issues, matches)
        
        ar_resources = existing["artifact-registry"]
        
        if repo_name in ar_resources:
            tfvars_path = self.output_dir / "artifact-registry" / repo_name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if repo_name in content:
                    matches.append(f"Repository '{repo_name}' configuration found and matches")
                else:
                    issues.append(f"Repository tfvars exists but name mismatch")
        else:
            issues.append(f"Repository '{repo_name}' not found in existing configurations")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "artifact_registry", repo_name, issues, matches)
    
    def _validate_workbench(self, instance_name: str, existing: Dict[str, Dict[str, List[str]]]) -> ValidationResult:
        """Validate Workbench configuration."""
        issues = []
        matches = []
        
        if "workbench" not in existing:
            issues.append("No Workbench configuration found")
            return ValidationResult(False, "workbench", instance_name, issues, matches)
        
        wb_resources = existing["workbench"]
        
        if instance_name in wb_resources:
            tfvars_path = self.output_dir / "workbench" / instance_name / "terraform.tfvars"
            if tfvars_path.exists():
                content = tfvars_path.read_text()
                if instance_name in content:
                    matches.append(f"Workbench '{instance_name}' configuration found and matches")
                else:
                    issues.append(f"Workbench tfvars exists but name mismatch")
        else:
            issues.append(f"Workbench '{instance_name}' not found in existing configurations")
        
        is_valid = len(issues) == 0 and len(matches) > 0
        return ValidationResult(is_valid, "workbench", instance_name, issues, matches)


def validate_existing(output_dir: str, spec: InfrastructureSpec) -> Tuple[bool, List[ValidationResult]]:
    """
    Validate existing Terraform files against specification.
    
    Args:
        output_dir: Directory containing generated files
        spec: Infrastructure specification
        
    Returns:
        Tuple of (all_valid, list of results)
    """
    validator = TerraformValidator(output_dir)
    results = validator.validate_against_spec(spec)
    
    all_valid = all(r.is_valid for r in results)
    return all_valid, results
