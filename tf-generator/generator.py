#!/usr/bin/env python3
"""
Enterprise Terraform Generator
===============================

Generates Terraform configuration files from TDA (Technical Design Authority) documents.

Usage:
    python generator.py [docx_file]                    # Separate folders (default)
    python generator.py [docx_file] --single-file      # All in one folder
    
If no docx_file is specified, the generator will look for .docx files in the current directory.

Author: Terraform Generator Team
Version: 1.1.0
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from parser import parse_docx, InfrastructureSpec
from templates import generate_all, generate_single_file, GeneratedFiles, SingleFileOutput
from validator import TerraformValidator, validate_existing
from config import DEFAULT_REGION


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print the application banner."""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   {Colors.BOLD}ENTERPRISE TERRAFORM GENERATOR{Colors.ENDC}{Colors.CYAN}                                  ║
║                                                                    ║
║   Generates Terraform files from TDA documents                     ║
║   Version 1.1.0                                                    ║
║                                                                    ║
╚══════════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.ENDC}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")


def find_docx_files(directory: str = ".") -> List[str]:
    """Find all .docx files in the specified directory."""
    return glob.glob(os.path.join(directory, "*.docx"))


def get_project_id() -> str:
    """Prompt user for GCP project ID."""
    print_section("Project Configuration")
    print_info("The GCP Project ID is required to generate Terraform files.")
    print_info("This is the unique identifier for your Google Cloud project.")
    print()
    
    while True:
        project_id = input(f"{Colors.BOLD}Enter GCP Project ID: {Colors.ENDC}").strip()
        
        if not project_id:
            print_error("Project ID cannot be empty. Please try again.")
            continue
        
        # Basic validation
        if not project_id.replace("-", "").replace("_", "").isalnum():
            print_warning("Project ID should contain only letters, numbers, hyphens, and underscores.")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        # Confirm
        print()
        print_info(f"Project ID: {Colors.BOLD}{project_id}{Colors.ENDC}")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm == 'y':
            return project_id
        
        print()


def display_extracted_spec(spec: InfrastructureSpec):
    """Display the extracted infrastructure specification."""
    print_section("Extracted Infrastructure Specification")
    
    print(f"\n{Colors.BOLD}VPC:{Colors.ENDC}")
    print(f"  Name: {spec.vpc_name or 'Not found'}")
    print(f"  Subnet: {spec.subnet_cidr or 'Not found'}")
    
    print(f"\n{Colors.BOLD}Service Account:{Colors.ENDC}")
    print(f"  Name: {spec.service_account_name or 'Not found'}")
    if spec.service_account_roles:
        print(f"  Roles:")
        for role in spec.service_account_roles:
            print(f"    - {role}")
    
    print(f"\n{Colors.BOLD}GCS Buckets:{Colors.ENDC}")
    if spec.bucket_names:
        for bucket in spec.bucket_names:
            print(f"  - {bucket}")
    else:
        print("  None found")
    
    print(f"\n{Colors.BOLD}Artifact Registry:{Colors.ENDC}")
    print(f"  Repository: {spec.artifact_registry_name or 'Not found'}")
    
    print(f"\n{Colors.BOLD}Workbench:{Colors.ENDC}")
    print(f"  Instance: {spec.workbench_name or 'Not found'}")
    print(f"  Network: {spec.workbench_network or 'Not found'}")


def write_terraform_files(output_dir: Path, resource_path: str, files: GeneratedFiles):
    """Write Terraform files to the output directory."""
    resource_dir = output_dir / resource_path
    resource_dir.mkdir(parents=True, exist_ok=True)
    
    # Write each file
    (resource_dir / "main.tf").write_text(files.main_tf)
    (resource_dir / "variables.tf").write_text(files.variables_tf)
    (resource_dir / "terraform.tfvars").write_text(files.terraform_tfvars)
    (resource_dir / "provider.tf").write_text(files.provider_tf)
    
    return resource_dir


def generate_terraform_files(spec: InfrastructureSpec, project_id: str, output_dir: Path):
    """Generate all Terraform files (separate folders mode)."""
    print_section("Generating Terraform Files (Separate Folders)")
    
    # Generate all files
    generated = generate_all(spec, project_id, DEFAULT_REGION)
    
    if not generated:
        print_warning("No resources found to generate. Please check your input document.")
        return
    
    # Write files
    for resource_path, files in generated.items():
        resource_dir = write_terraform_files(output_dir, resource_path, files)
        print_success(f"Generated: {resource_path}/")
        print(f"    ├── main.tf")
        print(f"    ├── variables.tf")
        print(f"    ├── terraform.tfvars")
        print(f"    └── provider.tf")
    
    print()
    print_success(f"All files written to: {output_dir}")


def generate_single_file_mode(spec: InfrastructureSpec, project_id: str, output_dir: Path):
    """Generate all Terraform files in a single folder."""
    print_section("Generating Terraform Files (Single Folder)")
    
    # Generate single file output
    output = generate_single_file(spec, project_id, DEFAULT_REGION)
    
    # Create output directory
    single_dir = output_dir / "infrastructure"
    single_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    (single_dir / "main.tf").write_text(output.main_tf)
    (single_dir / "variables.tf").write_text(output.variables_tf)
    (single_dir / "terraform.tfvars").write_text(output.terraform_tfvars)
    (single_dir / "provider.tf").write_text(output.provider_tf)
    (single_dir / "outputs.tf").write_text(output.outputs_tf)
    
    print_success(f"Generated: infrastructure/")
    print(f"    ├── main.tf          (all resources)")
    print(f"    ├── variables.tf     (all variables)")
    print(f"    ├── terraform.tfvars (all values)")
    print(f"    ├── provider.tf      (provider config)")
    print(f"    └── outputs.tf       (outputs)")
    
    print()
    print_success(f"All files written to: {single_dir}")
    
    return single_dir


def check_existing_files(output_dir: Path, spec: InfrastructureSpec) -> bool:
    """Check if existing files match the specification."""
    print_section("Checking Existing Files")
    
    if not output_dir.exists():
        print_info("No existing output directory found. Will create new files.")
        return False
    
    all_valid, results = validate_existing(str(output_dir), spec)
    
    if not results:
        print_info("No existing Terraform files found.")
        return False
    
    print(f"\n{Colors.BOLD}Validation Results:{Colors.ENDC}")
    
    for result in results:
        status = f"{Colors.GREEN}✓{Colors.ENDC}" if result.is_valid else f"{Colors.RED}✗{Colors.ENDC}"
        print(f"\n  {status} {result.resource_type}: {result.resource_name}")
        
        if result.matches:
            for match in result.matches:
                print(f"      {Colors.GREEN}+ {match}{Colors.ENDC}")
        
        if result.issues:
            for issue in result.issues:
                print(f"      {Colors.RED}- {issue}{Colors.ENDC}")
    
    if all_valid:
        print()
        print_success("All existing files are valid and match the specification.")
        return True
    else:
        print()
        print_warning("Some files need to be regenerated.")
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enterprise Terraform Generator - Generate TF files from TDA documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generator.py                           # Auto-find docx, separate folders
  python generator.py my_doc.docx               # Specify docx, separate folders
  python generator.py --single-file             # Auto-find docx, single folder
  python generator.py my_doc.docx --single-file # Specify docx, single folder
  python generator.py --dry-run                 # Preview without creating files
        """
    )
    parser.add_argument(
        "docx_file",
        nargs="?",
        help="Path to the DOCX document (optional, will auto-find if not specified)"
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        dest="single_file",
        help="Generate all resources in a single folder instead of separate folders"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Preview what would be generated without creating files"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    print_banner()
    
    # Show mode
    mode_parts = []
    if args.single_file:
        mode_parts.append("Single Folder")
    else:
        mode_parts.append("Separate Folders")
    if args.dry_run:
        mode_parts.append("DRY RUN")
    print_info(f"Mode: {' | '.join(mode_parts)}")
    
    # Determine the script directory
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    
    # Find DOCX file
    if args.docx_file:
        docx_file = args.docx_file
    else:
        docx_files = find_docx_files(str(script_dir))
        if not docx_files:
            print_error("No .docx files found in the current directory.")
            print_info("Usage: python generator.py [path/to/document.docx] [--single-file]")
            sys.exit(1)
        
        if len(docx_files) == 1:
            docx_file = docx_files[0]
        else:
            print_section("Select Input Document")
            for i, f in enumerate(docx_files, 1):
                print(f"  {i}. {os.path.basename(f)}")
            
            while True:
                try:
                    choice = int(input(f"\nSelect file (1-{len(docx_files)}): "))
                    if 1 <= choice <= len(docx_files):
                        docx_file = docx_files[choice - 1]
                        break
                except ValueError:
                    pass
                print_error("Invalid selection. Please try again.")
    
    print_section("Input Document")
    print_info(f"Processing: {docx_file}")
    
    # Parse the document
    try:
        spec = parse_docx(docx_file)
    except FileNotFoundError:
        print_error(f"File not found: {docx_file}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error parsing document: {e}")
        sys.exit(1)
    
    # Display extracted specification
    display_extracted_spec(spec)
    
    # Check if we have enough data
    if not any([spec.vpc_name, spec.bucket_names, spec.service_account_name, 
                spec.artifact_registry_name, spec.workbench_name]):
        print_error("No infrastructure resources found in the document.")
        print_info("Please ensure the document contains resource specifications.")
        sys.exit(1)
    
    # Check existing files (only for separate folders mode and not dry-run)
    if not args.single_file and not args.dry_run:
        files_valid = check_existing_files(output_dir, spec)
        
        if files_valid:
            print()
            regenerate = input("Files are valid. Regenerate anyway? (y/n): ").strip().lower()
            if regenerate != 'y':
                print_info("Keeping existing files.")
                sys.exit(0)
    
    # DRY RUN MODE
    if args.dry_run:
        print_section("Dry Run Preview")
        print_warning("DRY RUN - No files will be created")
        print()
        
        if args.single_file:
            print(f"{Colors.BOLD}Would generate in: {output_dir}/infrastructure/{Colors.ENDC}")
            print("  ├── main.tf          (all resources combined)")
            print("  ├── variables.tf     (all variables)")
            print("  ├── terraform.tfvars (all values)")
            print("  ├── provider.tf      (provider configuration)")
            print("  └── outputs.tf       (resource outputs)")
        else:
            print(f"{Colors.BOLD}Would generate in: {output_dir}/{Colors.ENDC}")
            print()
            
            if spec.vpc_name:
                print(f"  {Colors.GREEN}vpc/{spec.vpc_name}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
            
            if spec.subnet_cidr:
                subnet_name = spec.subnet_name or f"{spec.vpc_name}-subnet-01"
                print(f"  {Colors.GREEN}subnet/{subnet_name}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
            
            if spec.service_account_name:
                sa_name = spec.service_account_name.split("@")[0] if "@" in spec.service_account_name else spec.service_account_name
                print(f"  {Colors.GREEN}sa/{sa_name}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
            
            for bucket in spec.bucket_names:
                print(f"  {Colors.GREEN}gcs/{bucket}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
            
            if spec.artifact_registry_name:
                print(f"  {Colors.GREEN}artifact-registry/{spec.artifact_registry_name}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
            
            if spec.workbench_name:
                print(f"  {Colors.GREEN}workbench/{spec.workbench_name}/{Colors.ENDC}")
                print("    ├── main.tf, variables.tf, terraform.tfvars, provider.tf")
        
        # Count resources
        resource_count = sum([
            1 if spec.vpc_name else 0,
            1 if spec.subnet_cidr else 0,
            1 if spec.service_account_name else 0,
            len(spec.bucket_names),
            1 if spec.artifact_registry_name else 0,
            1 if spec.workbench_name else 0
        ])
        
        print()
        print_section("Dry Run Summary")
        print(f"  Resources: {resource_count}")
        print(f"  Files per resource: 4 (main.tf, variables.tf, terraform.tfvars, provider.tf)")
        print(f"  Total files: {resource_count * 4 if not args.single_file else 5}")
        print()
        print_info("To generate files, run without --dry-run flag")
        sys.exit(0)
    
    # Get project ID from user
    project_id = get_project_id()
    
    # Generate Terraform files based on mode
    if args.single_file:
        final_output_dir = generate_single_file_mode(spec, project_id, output_dir)
        
        # Single file summary
        print_section("Generation Complete")
        print(f"""
{Colors.BOLD}Next Steps:{Colors.ENDC}

1. Review the generated files in: {final_output_dir}

2. Deploy all resources at once:
   {Colors.CYAN}cd {final_output_dir}{Colors.ENDC}
   {Colors.CYAN}terraform init{Colors.ENDC}
   {Colors.CYAN}terraform plan{Colors.ENDC}
   {Colors.CYAN}terraform apply{Colors.ENDC}

{Colors.YELLOW}Note:{Colors.ENDC} Resources will be created in dependency order automatically.

{Colors.GREEN}Thank you for using Enterprise Terraform Generator!{Colors.ENDC}
""")
    else:
        generate_terraform_files(spec, project_id, output_dir)
        
        # Separate folders summary
        print_section("Generation Complete")
        print(f"""
{Colors.BOLD}Next Steps:{Colors.ENDC}

1. Review the generated files in: {output_dir}

2. Navigate to each resource directory and run:
   {Colors.CYAN}cd {output_dir}/<resource>{Colors.ENDC}
   {Colors.CYAN}terraform init{Colors.ENDC}
   {Colors.CYAN}terraform plan{Colors.ENDC}
   {Colors.CYAN}terraform apply{Colors.ENDC}

3. Recommended order of deployment:
   - VPC (networking foundation)
   - Subnet (network configuration)
   - Service Account (identity)
   - GCS Buckets (storage)
   - Artifact Registry (container images)
   - Workbench (compute)

{Colors.GREEN}Thank you for using Enterprise Terraform Generator!{Colors.ENDC}
""")


if __name__ == "__main__":
    main()

