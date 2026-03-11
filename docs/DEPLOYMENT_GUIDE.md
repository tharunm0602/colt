# GCP Infrastructure Deployment Guide

This guide provides step-by-step instructions for deploying the GCP sandbox infrastructure using Azure DevOps pipelines.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Bootstrap Deployment](#bootstrap-deployment)
- [Sandbox Deployment](#sandbox-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. GCP Organization Access
You need the following permissions at the **organization level**:
- `roles/resourcemanager.organizationAdmin` (or at minimum):
  - `resourcemanager.folders.create`
  - `resourcemanager.projects.create`
  - `billing.accounts.link`
- Organization ID: Get this from GCP Console → IAM & Admin → Settings

### 2. Azure DevOps Setup
- Azure DevOps Organization: **ColtProgrammeOffice**
- Project created in Azure DevOps
- Repository connected to this codebase

### 3. Required Information
Gather the following before starting:
- **GCP Organization ID**: `YOUR_ORG_ID`
- **GCP Billing Account ID**: `YOUR_BILLING_ACCOUNT_ID`
- **Azure DevOps Organization**: `ColtProgrammeOffice`
- **Azure DevOps Project Name**: Your project name
- **Azure DevOps Service Connection Name**: (will be created)

## Initial Setup

### Step 1: Configure Terraform Variables

Update the following `terraform.tfvars` files with your values:

#### 1.1 Bootstrap Folder
Edit `bootstrap/folder/terraform.tfvars`:
```hcl
org_id      = "YOUR_ORG_ID"          # Replace with your GCP org ID
folder_name = "sandbox-projects"
region      = "us-central1"
```

#### 1.2 Bootstrap Project
Edit `bootstrap/project/terraform.tfvars`:
```hcl
folder_id       = "folders/YOUR_FOLDER_ID"  # Will be output from folder step
project_name    = "colt-sandbox-infra"
project_id      = "colt-sbx-infra-001"
billing_account = "YOUR_BILLING_ACCOUNT_ID"  # Replace with billing account
region          = "us-central1"
```

#### 1.3 Bootstrap WIF
Edit `bootstrap/wif/terraform.tfvars`:
```hcl
project_id    = "colt-sbx-infra-001"
pool_id       = "azure-pool"
provider_id   = "azure-provider"
azure_org     = "ColtProgrammeOffice"
azure_subject = "sc://ColtProgrammeOffice/YOUR_PROJECT/YOUR_SERVICE_CONNECTION"
sa_id         = "projects/colt-sbx-infra-001/serviceAccounts/bootstrap-sa@colt-sbx-infra-001.iam.gserviceaccount.com"
region        = "us-central1"
```

#### 1.4 Bootstrap Folder IAM
Edit `bootstrap/folder-iam/terraform.tfvars`:
```hcl
folder_id      = "folders/YOUR_FOLDER_ID"  # Will be output from folder step
region         = "us-central1"

# Add team members who need viewer access
viewer_members = [
  "user:developer1@example.com",
  "group:dev-team@example.com",
]
```

### Step 2: Create Azure DevOps Variable Groups

Create two variable groups in Azure DevOps:

#### 2.1 Variable Group: `gcp-bootstrap-vars`
- Navigate to: Pipelines → Library → + Variable group
- Name: `gcp-bootstrap-vars`
- Variables:
  - `gcp-service-account-key`: (Base64 encoded service account key - initially use your own user credentials)

#### 2.2 Variable Group: `gcp-sandbox-vars`
- Name: `gcp-sandbox-vars`
- Variables:
  - `gcp-service-account-key`: (Will be populated after bootstrap completes)

### Step 3: Initial Authentication

For the **first bootstrap run**, you'll need to authenticate manually:

1. Create a temporary service account with org-level permissions:
```bash
# Set your org ID
export ORG_ID="YOUR_ORG_ID"
export INITIAL_PROJECT="YOUR_EXISTING_PROJECT"

# Create temp service account
gcloud iam service-accounts create bootstrap-init \
  --project=${INITIAL_PROJECT} \
  --display-name="Bootstrap Init SA"

# Grant org-level permissions
gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:bootstrap-init@${INITIAL_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.organizationAdmin"

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:bootstrap-init@${INITIAL_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/billing.user"

# Create and download key
gcloud iam service-accounts keys create bootstrap-key.json \
  --iam-account=bootstrap-init@${INITIAL_PROJECT}.iam.gserviceaccount.com

# Base64 encode and add to Azure DevOps variable group
cat bootstrap-key.json | base64
```

2. Add the base64-encoded key to `gcp-bootstrap-vars` → `gcp-service-account-key`

## Bootstrap Deployment

### Step 1: Create Azure DevOps Pipeline

1. In Azure DevOps, go to: Pipelines → New Pipeline
2. Select: Azure Repos Git (or your repo location)
3. Select your repository
4. Choose: Existing Azure Pipelines YAML file
5. Path: `/.azuredevops/pipelines/bootstrap-pipeline.yml`
6. Click: Run

### Step 2: Monitor Bootstrap Execution

The bootstrap pipeline will execute these stages in order:

1. **Create Backend Bucket** - Creates `build_logs_001` GCS bucket for Terraform state
2. **Bootstrap Folder** - Creates the sandbox folder in your org
3. **Bootstrap Project** - Creates the `colt-sbx-infra-001` project
4. **Bootstrap GCS** - Creates the Terraform state bucket
5. **Bootstrap Service Account** - Creates the service account for automation
6. **Bootstrap WIF** - Sets up Workload Identity Federation for Azure DevOps
7. **Bootstrap Folder IAM** - Grants viewer permissions at folder level

### Step 3: Configure Azure DevOps Service Connection

After the WIF stage completes, you'll see output with the WIF provider details:

1. In Azure DevOps, go to: Project Settings → Service connections → New service connection
2. Select: Google Cloud Platform
3. Authentication: Workload Identity Federation
4. Configuration:
   - **Issuer**: `https://vstoken.dev.azure.com/ColtProgrammeOffice`
   - **Subject Identifier**: `sc://ColtProgrammeOffice/YOUR_PROJECT/gcp-wif-connection`
   - **Workload Identity Pool Provider**: (from terraform output)
   - **Service Account Email**: `bootstrap-sa@colt-sbx-infra-001.iam.gserviceaccount.com`
5. Service connection name: `gcp-wif-connection`
6. Grant access permission to all pipelines

### Step 4: Update WIF Configuration

Update `bootstrap/wif/terraform.tfvars` with the actual service connection name:
```hcl
azure_subject = "sc://ColtProgrammeOffice/YOUR_PROJECT_NAME/gcp-wif-connection"
```

Re-run the WIF stage to update the binding.

## Sandbox Deployment

### Step 1: Create Sandbox Pipeline

1. In Azure DevOps, go to: Pipelines → New Pipeline
2. Select: Azure Repos Git
3. Select your repository
4. Choose: Existing Azure Pipelines YAML file
5. Path: `/.azuredevops/pipelines/sandbox-pipeline.yml`
6. Save (don't run yet)

### Step 2: Configure Automatic Triggers

The sandbox pipeline is configured to trigger automatically on:
- Changes to `sbx/**` directory
- Changes to `modules/**` directory
- Branches: `main`, `develop`

### Step 3: Initial Sandbox Deployment

1. Make a small change to any file in `sbx/` directory
2. Commit and push to `main` branch
3. Pipeline will automatically trigger and deploy:
   - Cloud Logging API
   - Cloud Monitoring API
   - GCS Storage Bucket
   - Service Account
   - Vertex AI API

### Step 4: Verify Deployment

After deployment completes:

```bash
# Set project
gcloud config set project colt-sbx-infra-001

# Check APIs enabled
gcloud services list --enabled

# Check storage buckets
gcloud storage buckets list

# Check service accounts
gcloud iam service-accounts list

# Check folder
gcloud resource-manager folders describe YOUR_FOLDER_ID
```

## Pipeline Configuration Details

### Bootstrap Pipeline
- **Trigger**: Manual only (for safety)
- **Stages**: 7 stages (sequential execution)
- **Deployment**: Runs once to set up infrastructure
- **Approval**: Auto-deploy (no manual gates)

### Sandbox Pipeline
- **Trigger**: Automatic on code changes
- **Stages**: Parallel plan, sequential deploy
- **Deployment**: Auto-deploy after successful plan
- **Approval**: None (auto-approve)

## Adding Team Members

To grant team members access to the sandbox folder:

1. Edit `bootstrap/folder-iam/terraform.tfvars`
2. Add users/groups to `viewer_members`:
```hcl
viewer_members = [
  "user:developer@example.com",
  "group:devteam@example.com",
]
```
3. Commit and push changes
4. Manually trigger bootstrap pipeline (or just the folder-iam stage)

## Folder-Level Permissions

The folder has viewer role granted to specified members. To add custom roles:

Edit `bootstrap/folder-iam/terraform.tfvars`:
```hcl
custom_role_bindings = {
  "editor_binding" = {
    role   = "roles/editor"
    member = "user:admin@example.com"
  }
  "sa_binding" = {
    role   = "roles/compute.admin"
    member = "serviceAccount:sa@project.iam.gserviceaccount.com"
  }
}
```

## Troubleshooting

### Issue: Backend bucket doesn't exist

**Error**: `Error: Failed to get existing workspaces: querying Cloud Storage failed`

**Solution**:
```bash
# Manually create the bucket
gcloud storage buckets create gs://build_logs_001 \
  --project=colt-sbx-infra-001 \
  --location=us-central1 \
  --uniform-bucket-level-access

# Or run the script
bash scripts/create-backend-bucket.sh
```

### Issue: Permission denied on folder creation

**Error**: `Error: Error creating Folder: googleapi: Error 403`

**Solution**: Ensure your service account has `roles/resourcemanager.folderCreator` at org level:
```bash
gcloud organizations add-iam-policy-binding YOUR_ORG_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/resourcemanager.folderCreator"
```

### Issue: WIF authentication fails

**Error**: `Error: google: could not find default credentials`

**Solution**:
1. Verify service connection is configured correctly
2. Check that `azure_subject` in WIF terraform matches service connection
3. Ensure service account has `roles/iam.workloadIdentityUser`

### Issue: Terraform state locked

**Error**: `Error: Error acquiring the state lock`

**Solution**:
```bash
cd path/to/module
terraform force-unlock LOCK_ID
```

### Issue: Project quota exceeded

**Error**: `Error: Error creating Project: quotaExceeded`

**Solution**: Request quota increase or use existing project

### Issue: Billing account permissions

**Error**: `Error: The caller does not have permission to link the billing account`

**Solution**: Grant `roles/billing.user` to your service account:
```bash
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/billing.user"
```

## Next Steps

After successful deployment:

1. **Add more environments**: Copy `sbx/` to `dev/`, `prod/` and create corresponding pipelines
2. **Enable more GCP services**: Add modules in `modules/` directory
3. **Configure monitoring**: Set up alerts and dashboards
4. **Document runbooks**: Create operational procedures
5. **Set up CI/CD**: Integrate application deployments

## Security Best Practices

1. **Never commit service account keys** to version control
2. **Use WIF** instead of service account keys where possible
3. **Rotate credentials** regularly (90-day cycle)
4. **Review IAM bindings** quarterly
5. **Enable audit logging** on all resources
6. **Use separate projects** for dev/staging/prod
7. **Implement least privilege** - grant minimum required permissions

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Azure DevOps pipeline logs
- Check Terraform state files in GCS bucket
- Review GCP Cloud Console for resource status
