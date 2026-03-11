# Colt - GCP Infrastructure as Code

Infrastructure as Code (IaC) for GCP sandbox environment using Terraform and automated with Azure DevOps pipelines.

## 🏗️ Project Overview

This repository contains Terraform configurations for deploying and managing GCP infrastructure with a focus on:
- **Sandbox environment** for development and testing
- **Automated deployments** via Azure DevOps pipelines
- **Workload Identity Federation** for secure, keyless authentication
- **Folder-level organization** with proper IAM controls

**Organization**: ColtProgrammeOffice  
**Primary Project**: colt-sbx-infra-001  
**Region**: us-central1

## 📁 Repository Structure

```
.
├── .azuredevops/
│   └── pipelines/
│       ├── bootstrap-pipeline.yml      # Bootstrap infrastructure (run once)
│       ├── sandbox-pipeline.yml        # Sandbox deployment (auto-triggered)
│       └── templates/                  # Reusable pipeline templates
├── bootstrap/
│   ├── folder/                         # GCP folder creation
│   ├── project/                        # Project creation
│   ├── gcs/                           # Terraform state bucket
│   ├── service-account/               # Service accounts
│   ├── wif/                           # Workload Identity Federation
│   └── folder-iam/                    # Folder-level IAM bindings
├── sbx/                               # Sandbox environment
│   ├── cloud-logging/
│   ├── cloud-monitoring/
│   ├── gcs/
│   ├── service-account/
│   └── vertex-ai/
├── modules/                           # Reusable Terraform modules
│   ├── gcs/
│   ├── vertex-ai/
│   ├── service-account/
│   └── ...
├── scripts/
│   └── create-backend-bucket.sh      # Backend bucket creation
└── docs/
    ├── DEPLOYMENT_GUIDE.md           # Step-by-step deployment guide
    └── AZURE_DEVOPS_SETUP.md         # Azure DevOps configuration
```

## 🚀 Quick Start

### Prerequisites

- GCP Organization with admin access
- Azure DevOps organization: **ColtProgrammeOffice**
- Terraform 1.6.0+
- gcloud CLI

### Initial Setup

1. **Configure variables** in `terraform.tfvars` files:
   ```bash
   # Update bootstrap/folder/terraform.tfvars
   org_id      = "YOUR_ORG_ID"
   folder_name = "sandbox-projects"
   
   # Update bootstrap/project/terraform.tfvars
   billing_account = "YOUR_BILLING_ACCOUNT_ID"
   ```

2. **Run bootstrap pipeline** (one-time):
   - Creates folder, project, service accounts, WIF
   - See: [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

3. **Deploy sandbox** automatically:
   - Pipeline triggers on changes to `sbx/` or `modules/`
   - Auto-deploys after successful plan

## 🎯 Infrastructure Components

### Bootstrap Layer
Infrastructure foundation that runs once:
- **Folder**: `sandbox-projects` folder in GCP org
- **Project**: `colt-sbx-infra-001` GCP project
- **Backend**: GCS bucket `build_logs_001` for Terraform state
- **Service Account**: Bootstrap SA with necessary permissions
- **WIF**: Azure DevOps ↔ GCP authentication
- **Folder IAM**: Viewer role for team members

### Sandbox Layer
Development/testing environment:
- **Cloud Logging**: Logging API enablement
- **Cloud Monitoring**: Monitoring API enablement
- **GCS Bucket**: Storage bucket for sandbox data
- **Service Account**: Sandbox service account with limited permissions
- **Vertex AI**: AI/ML platform API enablement

## 🔐 Authentication

Uses **Workload Identity Federation (WIF)** for keyless authentication:
- No service account keys stored in Azure DevOps
- Temporary tokens issued per pipeline run
- Azure DevOps → GCP trust relationship via OIDC

## 📊 Pipelines

### Bootstrap Pipeline
**File**: `.azuredevops/pipelines/bootstrap-pipeline.yml`  
**Trigger**: Manual only  
**Purpose**: One-time infrastructure setup

**Stages**:
1. Create backend bucket
2. Create folder
3. Create project
4. Create state bucket
5. Create service account
6. Configure WIF
7. Configure folder IAM

### Sandbox Pipeline
**File**: `.azuredevops/pipelines/sandbox-pipeline.yml`  
**Trigger**: Automatic on `main`/`develop` branches  
**Path Filters**: `sbx/**`, `modules/**`  
**Purpose**: Deploy sandbox infrastructure

**Stages**:
1. Validate all configurations
2. Plan all modules (parallel)
3. Deploy all modules (sequential)
4. Show deployment summary

## 🛠️ Common Commands

### Local Development

```bash
# Initialize Terraform
cd sbx/gcs
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Format code
terraform fmt -recursive

# Validate configuration
terraform validate
```

### Pipeline Operations

```bash
# Trigger sandbox pipeline manually
az pipelines run --name sandbox-pipeline

# View pipeline runs
az pipelines runs list --pipeline-name sandbox-pipeline

# Download pipeline logs
az pipelines runs show --id RUN_ID
```

### GCP Operations

```bash
# Set project
gcloud config set project colt-sbx-infra-001

# List enabled APIs
gcloud services list --enabled

# List buckets
gcloud storage buckets list

# View folder
gcloud resource-manager folders describe FOLDER_ID
```

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[Azure DevOps Setup](docs/AZURE_DEVOPS_SETUP.md)**: Pipeline configuration guide

## 🔄 Adding New Environments

To add dev/prod environments:

1. **Copy sandbox structure**:
   ```bash
   cp -r sbx/ dev/
   ```

2. **Update tfvars** in `dev/` with dev-specific values

3. **Create pipeline**:
   ```yaml
   # .azuredevops/pipelines/dev-pipeline.yml
   # Copy sandbox-pipeline.yml and update paths
   ```

4. **Update triggers** for dev environment

## 👥 Team Access

Folder-level permissions grant viewer access. To add team members:

1. Edit `bootstrap/folder-iam/terraform.tfvars`:
   ```hcl
   viewer_members = [
     "user:developer@example.com",
     "group:team@example.com",
   ]
   ```

2. Run bootstrap pipeline to apply changes

## 🐛 Troubleshooting

### Common Issues

**Backend bucket doesn't exist**
```bash
bash scripts/create-backend-bucket.sh
```

**Permission denied**
- Check service account IAM roles
- Verify WIF configuration
- Review folder-level permissions

**Terraform state locked**
```bash
terraform force-unlock LOCK_ID
```

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md#troubleshooting) for detailed troubleshooting.

## 🔒 Security

- ✅ Workload Identity Federation (no keys)
- ✅ Secrets stored in Azure DevOps variable groups
- ✅ Least-privilege IAM roles
- ✅ Folder-level access controls
- ✅ State files encrypted in GCS
- ✅ Uniform bucket-level access

## 📝 Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-module
   ```

2. **Make changes** to Terraform configs

3. **Test locally**:
   ```bash
   terraform plan
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add new module"
   git push origin feature/new-module
   ```

5. **Create PR** and merge to main

6. **Pipeline auto-deploys** on merge

## 🎓 Learning Resources

- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Azure Pipelines YAML](https://docs.microsoft.com/en-us/azure/devops/pipelines/yaml-schema)

## 📞 Support

For questions or issues:
1. Check documentation in `docs/`
2. Review pipeline logs in Azure DevOps
3. Check Terraform state in GCS bucket
4. Contact infrastructure team

## ✅ Verification Checklist

After deployment, verify:
- [ ] Folder created in GCP org
- [ ] Project `colt-sbx-infra-001` exists
- [ ] Backend bucket `build_logs_001` created
- [ ] Service accounts created
- [ ] WIF configured and working
- [ ] Folder IAM bindings applied
- [ ] Sandbox resources deployed
- [ ] Pipelines running successfully

## 🚦 Project Status

**Current Environment**: Sandbox  
**Status**: ✅ Active  
**Last Updated**: 2026-03-12  
**Terraform Version**: 1.6.0  
**GCP Provider Version**: 6.19+

---

**Maintained by**: Colt Infrastructure Team  
**Organization**: ColtProgrammeOffice