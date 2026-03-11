# Azure DevOps Setup Guide

Complete guide for setting up Azure DevOps pipelines with GCP Workload Identity Federation.

## Overview

This setup uses **Workload Identity Federation (WIF)** to authenticate Azure DevOps pipelines with GCP without storing service account keys.

**Organization**: ColtProgrammeOffice  
**Authentication Method**: WIF (Keyless)  
**GCP Project**: colt-sbx-infra-001

## Prerequisites

- Azure DevOps organization: **ColtProgrammeOffice**
- Azure DevOps project created
- Access to create service connections
- GCP organization admin access (for initial setup)

## Step-by-Step Setup

### Step 1: Create Azure DevOps Project

1. Navigate to https://dev.azure.com/ColtProgrammeOffice
2. Click **+ New Project**
3. Project name: `colt-infrastructure` (or your preferred name)
4. Visibility: Private
5. Click **Create**

### Step 2: Import Repository

1. Go to Repos → Files
2. Click **Import**
3. Repository type: Git
4. Clone URL: Your repository URL
5. Click **Import**

Alternatively, push your local repository:
```bash
cd /path/to/colt
git remote add azure https://ColtProgrammeOffice@dev.azure.com/ColtProgrammeOffice/colt-infrastructure/_git/colt
git push azure main
```

### Step 3: Create Variable Groups

#### Variable Group 1: gcp-bootstrap-vars

1. Navigate to: Pipelines → Library → + Variable group
2. Variable group name: `gcp-bootstrap-vars`
3. Add variables:
   - Name: `gcp-service-account-key`
   - Value: Base64-encoded service account key (temporary, for initial bootstrap)
   - Check: 🔒 Keep this value secret

#### Variable Group 2: gcp-sandbox-vars

1. Create another variable group
2. Variable group name: `gcp-sandbox-vars`
3. Add variables:
   - Name: `gcp-service-account-key`
   - Value: (Will be populated after WIF setup - leave empty for now)
   - Check: 🔒 Keep this value secret

### Step 4: Run Bootstrap Pipeline (First Time)

For the **first run only**, you need manual authentication:

#### 4.1 Create Temporary Service Account

```bash
# Set variables
export ORG_ID="YOUR_ORG_ID"
export TEMP_PROJECT="YOUR_EXISTING_PROJECT"  # Any existing project in your org

# Create temporary service account
gcloud iam service-accounts create azure-devops-init \
  --project=${TEMP_PROJECT} \
  --display-name="Azure DevOps Bootstrap Init"

# Grant organization-level permissions
gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.organizationAdmin"

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.folderCreator"

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectCreator"

# Grant billing permissions
gcloud billing accounts add-iam-policy-binding YOUR_BILLING_ACCOUNT_ID \
  --member="serviceAccount:azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/billing.user"

# Create and download key
gcloud iam service-accounts keys create /tmp/azure-init-key.json \
  --iam-account=azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com

# Base64 encode the key
cat /tmp/azure-init-key.json | base64 -w 0 > /tmp/azure-init-key-b64.txt

# Display the encoded key
cat /tmp/azure-init-key-b64.txt
```

#### 4.2 Add Key to Azure DevOps

1. Copy the base64-encoded key from `/tmp/azure-init-key-b64.txt`
2. In Azure DevOps: Pipelines → Library → `gcp-bootstrap-vars`
3. Edit variable `gcp-service-account-key`
4. Paste the base64-encoded key
5. Save

#### 4.3 Create Bootstrap Pipeline

1. Go to: Pipelines → New Pipeline
2. Select: Azure Repos Git
3. Select your repository: `colt`
4. Configure: Existing Azure Pipelines YAML file
5. Path: `/.azuredevops/pipelines/bootstrap-pipeline.yml`
6. Click: Save and Run

#### 4.4 Monitor Bootstrap Execution

The pipeline will create:
- ✅ Backend bucket (build_logs_001)
- ✅ Sandbox folder
- ✅ Project (colt-sbx-infra-001)
- ✅ Terraform state bucket
- ✅ Bootstrap service account
- ✅ **Workload Identity Federation pool and provider**
- ✅ Folder-level IAM bindings

### Step 5: Configure WIF Service Connection

After the bootstrap pipeline completes the WIF stage:

#### 5.1 Get WIF Provider Details

From the pipeline output, copy the WIF provider name. It will look like:
```
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/azure-pool/providers/azure-provider
```

#### 5.2 Create Service Connection

1. In Azure DevOps: Project Settings → Service connections
2. Click: **New service connection**
3. Select: **Google Cloud Platform**
4. Authentication method: **Workload Identity Federation**
5. Fill in:
   - **Project Id**: `colt-sbx-infra-001`
   - **Workload Identity Provider**: (paste from pipeline output)
   - **Service Account Email**: `bootstrap-sa@colt-sbx-infra-001.iam.gserviceaccount.com`
6. Service connection name: `gcp-wif-connection`
7. Description: `GCP WIF for sandbox infrastructure`
8. Check: ☑️ Grant access permission to all pipelines
9. Click: **Save**

#### 5.3 Test Service Connection

1. Click: **Verify**
2. Should show: ✅ Verification Succeeded

If verification fails:
- Check that the WIF provider name is correct
- Verify service account email is correct
- Ensure project ID is `colt-sbx-infra-001`

### Step 6: Update WIF Terraform Configuration

The WIF configuration needs the exact service connection identifier:

1. Edit `bootstrap/wif/terraform.tfvars`
2. Update `azure_subject`:
```hcl
azure_subject = "sc://ColtProgrammeOffice/YOUR_PROJECT_NAME/gcp-wif-connection"
```
Replace `YOUR_PROJECT_NAME` with your actual Azure DevOps project name.

3. Commit and push:
```bash
git add bootstrap/wif/terraform.tfvars
git commit -m "Update WIF azure_subject with service connection name"
git push azure main
```

4. Re-run the bootstrap pipeline (or just the WIF stage)

### Step 7: Remove Temporary Service Account

After WIF is configured and working:

```bash
# Delete the temporary service account key
rm /tmp/azure-init-key.json /tmp/azure-init-key-b64.txt

# Delete the temporary service account
gcloud iam service-accounts delete \
  azure-devops-init@${TEMP_PROJECT}.iam.gserviceaccount.com \
  --project=${TEMP_PROJECT}
```

### Step 8: Create Sandbox Pipeline

1. Go to: Pipelines → New Pipeline
2. Select: Azure Repos Git
3. Select your repository: `colt`
4. Configure: Existing Azure Pipelines YAML file
5. Path: `/.azuredevops/pipelines/sandbox-pipeline.yml`
6. Click: **Save** (don't run yet)

### Step 9: Configure Triggers

The sandbox pipeline is already configured with triggers:

**Automatic Triggers:**
- Branch: `main`, `develop`
- Path filters: `sbx/**`, `modules/**`

**Behavior:**
- Automatically runs when you push changes to sandbox or modules
- Auto-deploys after successful plan (no manual approval)

### Step 10: Test End-to-End

Make a test change to trigger the sandbox pipeline:

```bash
# Make a small change
echo "# Test" >> sbx/gcs/terraform.tfvars

# Commit and push
git add sbx/gcs/terraform.tfvars
git commit -m "Test pipeline trigger"
git push azure main
```

Watch the pipeline run automatically and deploy the sandbox infrastructure.

## Pipeline Templates

All pipelines use reusable templates in `.azuredevops/pipelines/templates/`:

- **setup-terraform.yml** - Installs Terraform and gcloud CLI
- **terraform-init.yml** - Initializes Terraform with backend
- **terraform-validate.yml** - Validates and format-checks
- **terraform-plan.yml** - Creates and publishes plan artifact
- **terraform-apply.yml** - Applies plan from artifact

## Variable Groups Reference

### gcp-bootstrap-vars
Used by: Bootstrap pipeline

| Variable | Description | Secret |
|----------|-------------|--------|
| gcp-service-account-key | Initial SA key (removed after WIF) | ✅ |

### gcp-sandbox-vars
Used by: Sandbox pipeline

| Variable | Description | Secret |
|----------|-------------|--------|
| gcp-service-account-key | WIF token (auto-populated) | ✅ |

## Security Best Practices

### ✅ Do's
- Use WIF for authentication (keyless)
- Store secrets in Azure DevOps variable groups
- Mark sensitive values as secret
- Grant service connection access only to specific pipelines
- Review pipeline runs regularly
- Use least-privilege IAM roles

### ❌ Don'ts
- Don't commit service account keys to git
- Don't share service connection credentials
- Don't grant org-wide access unnecessarily
- Don't skip approval gates for production
- Don't use the same service account for all environments

## Troubleshooting

### Issue: Pipeline can't find variable group

**Error**: `Variable group 'gcp-bootstrap-vars' could not be found`

**Solution**:
1. Verify variable group exists: Pipelines → Library
2. Check variable group name spelling
3. Ensure pipeline has access to variable group

### Issue: WIF authentication fails

**Error**: `Error: google: could not find default credentials`

**Solution**:
1. Verify service connection exists and is named `gcp-wif-connection`
2. Check WIF provider name matches terraform output
3. Verify `azure_subject` in WIF terraform matches service connection
4. Test service connection: Project Settings → Service connections → Verify

### Issue: Permission denied in GCP

**Error**: `Error 403: Permission denied`

**Solution**:
1. Check service account IAM roles in GCP
2. Verify service account email in service connection
3. Ensure WIF binding is correct
4. Check project ID matches everywhere

### Issue: Terraform state lock

**Error**: `Error acquiring the state lock`

**Solution**:
1. Check if another pipeline is running
2. If stuck, manually unlock:
```bash
cd bootstrap/folder
terraform force-unlock LOCK_ID
```

## Next Steps

After successful setup:

1. ✅ Bootstrap pipeline running successfully
2. ✅ WIF configured and working
3. ✅ Sandbox pipeline deploying automatically
4. 📝 Add more team members to folder IAM
5. 📝 Create dev and prod environments
6. 📝 Set up monitoring and alerting
7. 📝 Configure backup and disaster recovery

## Support Resources

- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)
- [GCP Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Terraform GCS Backend](https://www.terraform.io/docs/language/settings/backends/gcs.html)
- Internal deployment guide: `docs/DEPLOYMENT_GUIDE.md`
