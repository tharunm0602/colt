"""
DOCX Parser Module - Extracts infrastructure details from TDA documents.
Uses docx2python for robust table extraction.
Improved: Uses configurable patterns instead of hardcoded regex.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from docx2python import docx2python

from config import NAMING_PATTERNS, ROLE_PATTERN


@dataclass
class InfrastructureSpec:
    """Data class to hold extracted infrastructure specifications."""
    vpc_name: Optional[str] = None
    subnet_cidr: Optional[str] = None
    subnet_name: Optional[str] = None
    service_account_name: Optional[str] = None
    service_account_roles: List[str] = field(default_factory=list)
    bucket_names: List[str] = field(default_factory=list)
    workbench_name: Optional[str] = None
    workbench_network: Optional[str] = None
    artifact_registry_name: Optional[str] = None
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy access."""
        return {
            "vpc_name": self.vpc_name,
            "subnet_cidr": self.subnet_cidr,
            "subnet_name": self.subnet_name,
            "service_account_name": self.service_account_name,
            "service_account_roles": self.service_account_roles,
            "bucket_names": self.bucket_names,
            "workbench_name": self.workbench_name,
            "workbench_network": self.workbench_network,
            "artifact_registry_name": self.artifact_registry_name
        }
    
    def get_missing_required(self) -> List[str]:
        """Return list of missing required fields."""
        missing = []
        if not self.vpc_name:
            missing.append("VPC Name")
        if not self.service_account_name:
            missing.append("Service Account")
        return missing
    
    def validate_dependencies(self) -> List[str]:
        """Check if resource dependencies are satisfied."""
        issues = []
        
        # Workbench requires VPC
        if self.workbench_name and not self.vpc_name:
            issues.append("Workbench requires a VPC but none was found")
        
        # Subnet requires VPC
        if self.subnet_cidr and not self.vpc_name:
            issues.append("Subnet CIDR found but no VPC name")
        
        return issues


class DocxParser:
    """Parser for extracting infrastructure specs from DOCX files."""
    
    def __init__(self, docx_path: str, patterns=None):
        """
        Initialize parser with path to DOCX file.
        
        Args:
            docx_path: Path to the DOCX file to parse
            patterns: Optional custom NamingPatterns (uses default if not provided)
        """
        self.docx_path = Path(docx_path)
        if not self.docx_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        self.patterns = patterns or NAMING_PATTERNS
        self.doc = None
        self.raw_text = ""
        self.spec = InfrastructureSpec()
    
    def parse(self) -> InfrastructureSpec:
        """
        Parse the DOCX file and extract infrastructure specifications.
        
        Returns:
            InfrastructureSpec object with extracted values
        """
        # Extract all text from document
        self._extract_text()
        
        # Extract specific values using configurable patterns
        self._extract_vpc()
        self._extract_subnet()
        self._extract_service_account()
        self._extract_buckets()
        self._extract_workbench()
        self._extract_artifact_registry()
        
        self.spec.raw_text = self.raw_text
        return self.spec
    
    def _extract_text(self) -> None:
        """Extract all text from the DOCX file including tables."""
        doc = docx2python(str(self.docx_path))
        
        # Flatten the nested structure to get all text
        all_text = []
        
        def flatten(item):
            """Recursively flatten nested lists."""
            if isinstance(item, str):
                all_text.append(item)
            elif isinstance(item, list):
                for sub_item in item:
                    flatten(sub_item)
        
        # Process body content
        flatten(doc.body)
        
        # Join all text
        self.raw_text = "\n".join(filter(None, all_text))
    
    def _find_first_match(self, patterns: List[str], text: str = None) -> Optional[str]:
        """
        Find first match from a list of patterns.
        
        Args:
            patterns: List of regex patterns to try
            text: Text to search (uses self.raw_text if not provided)
            
        Returns:
            First matched string or None
        """
        search_text = text or self.raw_text
        
        for pattern in patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                # Return the captured group if exists, else full match
                try:
                    return match.group(1)
                except IndexError:
                    return match.group(0)
        
        return None
    
    def _find_all_matches(self, patterns: List[str], text: str = None) -> List[str]:
        """
        Find all matches from a list of patterns.
        
        Args:
            patterns: List of regex patterns to try
            text: Text to search (uses self.raw_text if not provided)
            
        Returns:
            List of all matched strings
        """
        search_text = text or self.raw_text
        matches = set()
        
        for pattern in patterns:
            found = re.findall(pattern, search_text, re.IGNORECASE)
            for match in found:
                if isinstance(match, tuple):
                    # If pattern has groups, take first non-empty
                    for m in match:
                        if m:
                            matches.add(m)
                            break
                elif isinstance(match, str) and match:
                    matches.add(match)
        
        return list(matches)
    
    def _extract_vpc(self) -> None:
        """Extract VPC name from document using configurable patterns."""
        patterns = self.patterns.get_vpc_patterns()
        
        match = self._find_first_match(patterns)
        if match:
            self.spec.vpc_name = match
    
    def _extract_subnet(self) -> None:
        """Extract subnet CIDR and generate subnet name."""
        # CIDR pattern is universal
        cidr_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})"
        match = re.search(cidr_pattern, self.raw_text)
        
        if match:
            self.spec.subnet_cidr = match.group(1)
            # Generate subnet name based on VPC name
            if self.spec.vpc_name:
                self.spec.subnet_name = f"{self.spec.vpc_name}-subnet-01"
            else:
                self.spec.subnet_name = "subnet-01"
    
    def _extract_service_account(self) -> None:
        """Extract service account name and roles using configurable patterns."""
        patterns = self.patterns.get_sa_patterns()
        
        # First check for PROJECT_ID placeholder pattern
        placeholder_pattern = rf"({self.patterns.org_prefix}-[a-zA-Z0-9-]*)<<PROJECT_ID>>@"
        match = re.search(placeholder_pattern, self.raw_text)
        
        if match:
            # Extract the prefix before PROJECT_ID
            prefix = match.group(1)
            # If prefix is just "sbx-colt-", use default SA name
            if prefix.endswith("-"):
                self.spec.service_account_name = f"{self.patterns.org_prefix}-sa"
            else:
                self.spec.service_account_name = prefix
        else:
            # Try other patterns
            match = self._find_first_match(patterns)
            if match:
                # Clean up the match (remove @domain if present)
                sa_name = match.split("@")[0] if "@" in match else match
                self.spec.service_account_name = sa_name
        
        # Extract roles
        roles = re.findall(ROLE_PATTERN, self.raw_text)
        if roles:
            # Deduplicate and format
            unique_roles = list(set([f"roles/{role}" for role in roles]))
            self.spec.service_account_roles = sorted(unique_roles)
    
    def _extract_buckets(self) -> None:
        """Extract GCS bucket names using configurable patterns."""
        patterns = self.patterns.get_bucket_patterns()
        
        matches = self._find_all_matches(patterns)
        
        # Words to exclude (labels, not actual bucket names)
        exclude_words = {"bucket", "buckets", "gcs", "storage", "data", "name", "names"}
        
        # Filter out obvious non-bucket matches
        buckets = set()
        for match in matches:
            # Skip if it looks like a role or other resource
            if "roles/" in match or "@" in match:
                continue
            # Skip if too short
            if len(match) < 5:
                continue
            # Skip generic words
            if match.lower() in exclude_words:
                continue
            # Skip if it doesn't have a hyphen (likely not a resource name)
            if "-" not in match:
                continue
            buckets.add(match)
        
        self.spec.bucket_names = sorted(list(buckets))
    
    def _extract_workbench(self) -> None:
        """Extract Workbench instance details using configurable patterns."""
        patterns = self.patterns.get_workbench_patterns()
        
        match = self._find_first_match(patterns)
        if match:
            self.spec.workbench_name = match
        
        # Extract network attachment
        network_patterns = [
            r"attach to\s+([a-zA-Z0-9-_]+)",
            r"Network[:\s|]+([a-zA-Z0-9-_]+)",
            r"VPC[:\s|]+([a-zA-Z0-9-_]+)",
        ]
        
        match = self._find_first_match(network_patterns)
        if match:
            self.spec.workbench_network = match
        
        # Fall back to VPC name if found
        if not self.spec.workbench_network and self.spec.vpc_name:
            self.spec.workbench_network = self.spec.vpc_name
    
    def _extract_artifact_registry(self) -> None:
        """Extract Artifact Registry repository name using configurable patterns."""
        patterns = self.patterns.get_artifact_patterns()
        
        match = self._find_first_match(patterns)
        if match:
            self.spec.artifact_registry_name = match


def parse_docx(docx_path: str, patterns=None) -> InfrastructureSpec:
    """
    Convenience function to parse a DOCX file.
    
    Args:
        docx_path: Path to the DOCX file
        patterns: Optional custom NamingPatterns
        
    Returns:
        InfrastructureSpec with extracted values
    """
    parser = DocxParser(docx_path, patterns)
    return parser.parse()


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        docx_file = sys.argv[1]
    else:
        # Default test file
        docx_file = "tda_cab_TDA-2026-001_20260107_170244 1.docx"
    
    print(f"Parsing: {docx_file}")
    print("-" * 50)
    
    spec = parse_docx(docx_file)
    
    print("Extracted Infrastructure Specification:")
    print(f"  VPC Name: {spec.vpc_name}")
    print(f"  Subnet CIDR: {spec.subnet_cidr}")
    print(f"  Subnet Name: {spec.subnet_name}")
    print(f"  Service Account: {spec.service_account_name}")
    print(f"  SA Roles: {spec.service_account_roles}")
    print(f"  Buckets: {spec.bucket_names}")
    print(f"  Workbench: {spec.workbench_name}")
    print(f"  Workbench Network: {spec.workbench_network}")
    print(f"  Artifact Registry: {spec.artifact_registry_name}")
    
    # Check for issues
    missing = spec.get_missing_required()
    if missing:
        print(f"\n⚠️  Missing required fields: {missing}")
    
    dep_issues = spec.validate_dependencies()
    if dep_issues:
        print(f"\n⚠️  Dependency issues:")
        for issue in dep_issues:
            print(f"    - {issue}")
