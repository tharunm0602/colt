# Enterprise Terraform Generator

A Python-based tool that automatically generates Terraform configuration files from TDA (Technical Design Authority) documents. Available as both a CLI tool and a Streamlit web application.

---

## Features

- **Document Parsing** - Extracts infrastructure specs from `.docx` files
- **Template-Based Generation** - Uses existing Terraform modules from the repository
- **Web UI** - Streamlit-based interface for easy use
- **CLI** - Command-line interface for automation
- **Multiple Resources** - VPC, Subnet, Service Account, GCS, Artifact Registry, Workbench

---

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Option 1: Web UI (Streamlit)

```bash
cd tf-generator
streamlit run app.py
```

Open http://localhost:8501 and:
1. Select a TDA document from the dropdown
2. Choose environment (dev/prod)
3. Select technology stack
4. Enter your GCP Project ID
5. Click **Generate Terraform**
6. View files in tabs, download as ZIP

### Option 2: CLI

```bash
cd tf-generator
python generator.py
```

---

## Project Structure

```
tf-generator/
├── app.py           # Streamlit web UI
├── generator.py     # CLI interface
├── parser.py        # DOCX parsing logic
├── templates.py     # Terraform file generation
├── validator.py     # File validation
├── config.py        # Default values & patterns
├── requirements.txt # Python dependencies
├── README.md        # This file
└── output/          # Generated Terraform files
```

---

## Generated Files

For each resource, the generator creates:

| File | Purpose |
|------|---------|
| `main.tf` | Module invocation |
| `variables.tf` | Variable definitions |
| `terraform.tfvars` | Environment-specific values |
| `provider.tf` | GCS backend + provider config |

---

## Output Structure

```
output/
├── vpc/{vpc_name}/
├── subnet/{subnet_name}/
├── sa/{sa_name}/
├── gcs/{bucket_name}/
├── artifact-registry/{repo_name}/
└── workbench/{instance_name}/
```

---

## Supported Resources

| Resource | Extracted From Document |
|----------|------------------------|
| VPC | `*-vpc` pattern |
| Subnet | CIDR notation (e.g., `10.0.0.0/24`) |
| Service Account | `*-sa@*.iam.gserviceaccount.com` |
| GCS Bucket | `*-data`, `*-bucket`, `*-storage` patterns |
| Artifact Registry | `*-artifact*`, `*-registry*` patterns |
| Workbench | `*-workbench*`, `*-notebook*` patterns |

---

## Deployment Order

Deploy resources in this order:

1. **VPC** - Network foundation
2. **Subnet** - Requires VPC
3. **Service Account** - IAM identity
4. **GCS Buckets** - Storage
5. **Artifact Registry** - Container images
6. **Workbench** - Requires VPC + Subnet

---

## Verification

After generation, validate with:

```bash
cd output/vpc/your-vpc-name
terraform init
terraform validate
terraform plan
```

---

## Configuration

Edit `config.py` to customize:

- `NAMING_PATTERNS` - Regex patterns for resource extraction
- `DEFAULTS` - Default values for each resource type
- `BACKEND_BUCKET` - GCS bucket for Terraform state
- `GOOGLE_PROVIDER_VERSION` - Provider version constraints

---

## Test Documents

Included test files for verification:
- `test_ecommerce_tda.docx` - E-commerce platform infrastructure
- `test_analytics_tda.docx` - Analytics platform infrastructure
