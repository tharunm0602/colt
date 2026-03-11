# Getting Started - Complete Setup Guide

**For Beginners**: This guide walks you through setting up GCP infrastructure with Azure DevOps from scratch.

---

## ⏱️ Time Required
- **Manual setup**: 30-45 minutes
- **Bootstrap pipeline**: 15-20 minutes
- **Total**: ~1 hour

## 📋 What You'll Need

Before starting, gather these:
- [ ] GCP Organization ID
- [ ] GCP Billing Account ID
- [ ] Access to create resources in GCP
- [ ] Azure DevOps organization: **ColtProgrammeOffice**
- [ ] Terminal with gcloud CLI installed

---

## Part 1: GCP Manual Setup (30 minutes)

### Step 1: Get Your GCP Organization and Billing IDs

Open your terminal and run:

```bash
# Login to GCP
gcloud auth login

# Get your organization ID
gcloud organizations list
```

You'll see output like:
```
DISPLAY_NAME        ID              DIRECTORY_CUSTOMER_ID
Your Company        123456789012    C012abc34
```

**Copy the ID** (numeric value) - this is your **Organization ID**.

Now get your billing account:

```bash
# List billing accounts
gcloud billing accounts list
```

You'll see:
```
ACCOUNT_ID            NAME                OPEN   MASTER_ACCOUNT_ID
012345-6789AB-CDEF01  My Billing Account  True
```

**Copy the ACCOUNT_ID** - this is your **Billing Account ID**.

**✏️ Write these down:**
- Organization ID: `_________________`
- Billing Account ID: `_________________`

---

### Step 2: Set Up Variables in Your Terminal

Copy and paste this, replacing with YOUR values:

```bash
# Set your values here (REPLACE THESE!)
export ORG_ID="123456789012"                    # Your org ID from Step 1
export BILLING_ACCOUNT_ID="012345-6789AB-CDEF01" # Your billing ID from Step 1
export TEMP_PROJECT="my-existing-project"        # Any existing project in your org

# Display to verify
echo "Organization ID: ${ORG_ID}"
echo "Billing Account: ${BILLING_ACCOUNT_ID}"
echo "Temp Project: ${TEMP_PROJECT}"
```

**⚠️ Important**: Replace the values above with YOUR actual IDs before running!

---

### Step 3: Create Temporary Service Account

This service account will be used only for the initial bootstrap, then deleted.

```bash
# Create the service account
gcloud iam service-accounts create bootstrap-init \
  --project=${TEMP_PROJECT} \
  --display-name="Bootstrap Initial Setup"

# Grant organization permissions
echo "Granting organization permissions..."

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.organizationAdmin"

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.folderCreator"

gcloud organizations add-iam-policy-binding ${ORG_ID} \
  --member="serviceAccount:bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectCreator"

# Grant billing permissions
echo "Granting billing permissions..."

gcloud billing accounts add-iam-policy-binding ${BILLING_ACCOUNT_ID} \
  --member="serviceAccount:bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/billing.user"

echo "✅ Service account created and permissions granted!"
```

---

### Step 4: Create and Encode Service Account Key

```bash
# Create the key file
gcloud iam service-accounts keys create ~/bootstrap-init-key.json \
  --iam-account=bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com

# Base64 encode it for Azure DevOps
cat ~/bootstrap-init-key.json | base64 > ~/bootstrap-init-key-b64.txt

echo ""
echo "=========================================="
echo "SERVICE ACCOUNT KEY (Base64 Encoded)"
echo "=========================================="
echo ""
cat ~/bootstrap-init-key-b64.txt
echo ""
echo "=========================================="
echo "Copy the text above ⬆️  You'll need it in Part 2"
echo "=========================================="
```

**📋 Copy the entire base64 text** - you'll paste this into Azure DevOps in Part 2.

---

### Step 5: Update Terraform Configuration Files

Open these files in your code editor and update with YOUR values:

#### File 1: `bootstrap/folder/terraform.tfvars`

```hcl
org_id      = "123456789012"      # ⬅️ YOUR ORG_ID from Step 1
folder_name = "sandbox-projects"
region      = "us-central1"
```

#### File 2: `bootstrap/project/terraform.tfvars`

```hcl
folder_id       = "folders/YOUR_FOLDER_ID"  # ⬅️ Leave this, will update later
project_name    = "colt-sandbox-infra"
project_id      = "colt-sbx-infra-001"
billing_account = "012345-6789AB-CDEF01"    # ⬅️ YOUR BILLING_ACCOUNT_ID from Step 1
region          = "us-central1"
```

#### File 3: `bootstrap/gcs/terraform.tfvars`

```hcl
project_id  = "colt-sbx-infra-001"
bucket_name = "colt-terraform-state-sandbox"
region      = "us-central1"
```

#### File 4: `bootstrap/service-account/terraform.tfvars`

```hcl
project_id   = "colt-sbx-infra-001"
sa_name      = "bootstrap-sa"
display_name = "Bootstrap Service Account"
region       = "us-central1"
```

#### File 5: `bootstrap/wif/terraform.tfvars`

```hcl
project_id    = "colt-sbx-infra-001"
pool_id       = "azure-pool"
provider_id   = "azure-provider"
azure_org     = "ColtProgrammeOffice"
azure_subject = "sc://ColtProgrammeOffice/YOUR_PROJECT_NAME/gcp-wif-connection"  # ⬅️ Update after creating Azure project
sa_id         = "projects/colt-sbx-infra-001/serviceAccounts/bootstrap-sa@colt-sbx-infra-001.iam.gserviceaccount.com"
region        = "us-central1"
```

**✅ Save all files** after updating.

---

## Part 2: Azure DevOps Setup (15 minutes)

### Step 6: Create Azure DevOps Project

1. Open browser: https://dev.azure.com/ColtProgrammeOffice
2. Click **+ New Project**
3. Fill in:
   - **Project name**: `colt-infrastructure` (or your choice)
   - **Visibility**: Private
4. Click **Create**

**📝 Write down your project name**: `_________________`

---

### Step 7: Import Code Repository

#### Option A: Import from Git

1. In your new project, go to **Repos** → **Files**
2. Click **Import**
3. Select **Git**
4. Enter your repository URL
5. Click **Import**

#### Option B: Push from Local

```bash
cd /Users/jabir/Documents/dev/prodapt/colt

# Add Azure DevOps remote (replace YOUR_PROJECT with your actual project name)
git remote add azure https://ColtProgrammeOffice@dev.azure.com/ColtProgrammeOffice/YOUR_PROJECT/_git/colt

# Push to Azure DevOps
git push azure main
```

---

### Step 8: Create Variable Groups

#### Variable Group 1: gcp-bootstrap-vars

1. Go to: **Pipelines** → **Library** → **+ Variable group**
2. Variable group name: `gcp-bootstrap-vars`
3. Click **+ Add** to add variable:
   - **Name**: `gcp-service-account-key`
   - **Value**: (Paste the base64 text from Step 4)
   - **Click the lock icon** 🔒 to make it secret
4. Click **Save**

#### Variable Group 2: gcp-sandbox-vars

1. Click **+ Variable group** again
2. Variable group name: `gcp-sandbox-vars`
3. Click **+ Add**:
   - **Name**: `gcp-service-account-key`
   - **Value**: (Leave empty for now)
   - **Click the lock icon** 🔒 to make it secret
4. Click **Save**

**✅ You should now have 2 variable groups**

---

### Step 9: Update WIF Configuration

Now that you know your Azure DevOps project name, update the WIF config:

Edit `bootstrap/wif/terraform.tfvars`:

```hcl
azure_subject = "sc://ColtProgrammeOffice/colt-infrastructure/gcp-wif-connection"
#                                         ^^^^^^^^^^^^^^^^^^^
#                                         Replace with YOUR project name from Step 6
```

**Save the file** and commit:

```bash
git add bootstrap/wif/terraform.tfvars
git commit -m "Update WIF with Azure DevOps project name"
git push azure main
```

---

## Part 3: Run Bootstrap Pipeline (20 minutes)

### Step 10: Create Bootstrap Pipeline

1. In Azure DevOps, go to **Pipelines** → **Pipelines**
2. Click **New Pipeline**
3. Select: **Azure Repos Git**
4. Select your repository: **colt**
5. Select: **Existing Azure Pipelines YAML file**
6. Path: `/.azuredevops/pipelines/bootstrap-pipeline.yml`
7. Click **Continue**
8. Click **Run**

**🎬 Pipeline is now running!** This will take about 15-20 minutes.

---

### Step 11: Monitor Bootstrap Progress

Watch the pipeline run through these stages:

1. ✅ **Create Backend Bucket** - Creates `build_logs_001`
2. ✅ **Bootstrap Folder** - Creates `sandbox-projects` folder
3. ✅ **Bootstrap Project** - Creates `colt-sbx-infra-001` project
4. ✅ **Bootstrap GCS** - Creates Terraform state bucket
5. ✅ **Bootstrap Service Account** - Creates service account
6. ✅ **Bootstrap WIF** - Sets up Workload Identity Federation
7. ✅ **Bootstrap Folder IAM** - Grants viewer permissions

**Wait for all stages to complete** (green checkmarks).

---

### Step 12: Get Folder ID from Output

After the "Bootstrap Folder" stage completes:

1. Click on the **BootstrapFolder** stage
2. Click on the **Terraform Apply** task
3. Scroll to the bottom of the logs
4. Look for output like:

```
Outputs:

folder_id = "folders/123456789012"
```

**Copy the folder ID** (including "folders/").

---

### Step 13: Update Project Configuration with Folder ID

Edit `bootstrap/project/terraform.tfvars`:

```hcl
folder_id       = "folders/123456789012"  # ⬅️ Paste YOUR folder_id from Step 12
project_name    = "colt-sandbox-infra"
project_id      = "colt-sbx-infra-001"
billing_account = "012345-6789AB-CDEF01"
region          = "us-central1"
```

Commit and push:

```bash
git add bootstrap/project/terraform.tfvars
git commit -m "Update folder_id after bootstrap"
git push azure main
```

---

### Step 14: Re-run Bootstrap for Project Creation

Since the project needs the folder ID, re-run the bootstrap:

1. Go to **Pipelines** → **Pipelines**
2. Click on your **bootstrap-pipeline**
3. Click **Run pipeline**
4. Click **Run**

This time it will:
- Skip folder (already exists)
- ✅ Create project with correct folder
- ✅ Complete remaining setup

---

### Step 15: Configure WIF Service Connection

After WIF stage completes, get the WIF provider name from logs:

1. Click on **BootstrapWIF** stage
2. Click on **Output WIF Configuration** task
3. Copy the **workload_identity_provider_name** value

It looks like:
```
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/azure-pool/providers/azure-provider
```

Now create the service connection:

1. Go to **Project Settings** (bottom left gear icon)
2. Select **Service connections**
3. Click **New service connection**
4. Select **Google Cloud Platform**
5. Select **Workload Identity Federation**
6. Fill in:
   - **Project Id**: `colt-sbx-infra-001`
   - **Workload Identity Provider**: (paste from logs above)
   - **Service Account Email**: `bootstrap-sa@colt-sbx-infra-001.iam.gserviceaccount.com`
7. Service connection name: `gcp-wif-connection`
8. Check: ☑️ **Grant access permission to all pipelines**
9. Click **Save**
10. Click **Verify** to test

**✅ Should show "Verification Succeeded"**

---

## Part 4: Deploy Sandbox (Auto) (5 minutes)

### Step 16: Create Sandbox Pipeline

1. Go to **Pipelines** → **Pipelines**
2. Click **New Pipeline**
3. Select: **Azure Repos Git**
4. Select: **colt**
5. Select: **Existing Azure Pipelines YAML file**
6. Path: `/.azuredevops/pipelines/sandbox-pipeline.yml`
7. Click **Continue**
8. Click **Save** (don't run yet)

---

### Step 17: Test Sandbox Deployment

The sandbox pipeline triggers automatically on code changes. Let's test it:

```bash
# Make a small change to trigger the pipeline
echo "# Sandbox ready" >> sbx/gcs/terraform.tfvars

# Commit and push
git add sbx/gcs/terraform.tfvars
git commit -m "Test sandbox pipeline trigger"
git push azure main
```

**🎬 Pipeline automatically triggers!**

Watch it deploy:
- ✅ Cloud Logging
- ✅ Cloud Monitoring
- ✅ GCS Bucket
- ✅ Service Account
- ✅ Vertex AI

---

### Step 18: Verify Deployment in GCP

```bash
# Set your project
gcloud config set project colt-sbx-infra-001

# Check enabled APIs
gcloud services list --enabled | grep -E "logging|monitoring|aiplatform"

# Check storage buckets
gcloud storage buckets list

# Check service accounts
gcloud iam service-accounts list
```

You should see all resources created!

---

## Part 5: Cleanup Initial Service Account

### Step 19: Remove Temporary Service Account

Now that WIF is working, delete the temporary service account:

```bash
# Delete the key files
rm ~/bootstrap-init-key.json
rm ~/bootstrap-init-key-b64.txt

# Delete the service account
gcloud iam service-accounts delete \
  bootstrap-init@${TEMP_PROJECT}.iam.gserviceaccount.com \
  --project=${TEMP_PROJECT} \
  --quiet

echo "✅ Temporary service account deleted!"
```

---

## 🎉 You're Done!

### What You've Accomplished

✅ **GCP Infrastructure**:
- Folder: `sandbox-projects`
- Project: `colt-sbx-infra-001`
- Service accounts with proper IAM
- Workload Identity Federation configured

✅ **Azure DevOps**:
- Bootstrap pipeline (runs once)
- Sandbox pipeline (auto-deploys on changes)
- Secure keyless authentication via WIF

✅ **Sandbox Environment**:
- Cloud Logging enabled
- Cloud Monitoring enabled
- GCS storage bucket
- Vertex AI ready

---

## 📚 Next Steps

### Add Team Members

Edit `bootstrap/folder-iam/terraform.tfvars`:

```hcl
viewer_members = [
  "user:teammate@example.com",
  "group:dev-team@example.com",
]
```

Then re-run bootstrap pipeline.

### Make Changes to Sandbox

Any changes to `sbx/**` or `modules/**` will automatically trigger deployment:

```bash
# Edit any file in sbx/
git add .
git commit -m "Update sandbox config"
git push azure main
# Pipeline runs automatically!
```

---

## ❓ Troubleshooting

### Pipeline Fails: "Permission Denied"

**Check**: Service account has org-level permissions
```bash
gcloud organizations get-iam-policy ${ORG_ID} \
  --filter="bindings.members:bootstrap-init@"
```

### Pipeline Fails: "Backend bucket doesn't exist"

**Run**:
```bash
bash scripts/create-backend-bucket.sh
```

### WIF Verification Fails

**Check**:
1. Service connection name is exactly `gcp-wif-connection`
2. WIF provider path is correct
3. Service account email is correct
4. Project ID is `colt-sbx-infra-001`

### Terraform State Locked

**Fix**:
```bash
cd bootstrap/folder
terraform force-unlock LOCK_ID
```

---

## 🆘 Need Help?

1. Check pipeline logs in Azure DevOps
2. Review detailed docs:
   - `docs/DEPLOYMENT_GUIDE.md` - Full deployment reference
   - `docs/AZURE_DEVOPS_SETUP.md` - Azure DevOps details
3. Check GCP Console for resource status

---

## ✅ Verification Checklist

After completing all steps, verify:

- [ ] Folder `sandbox-projects` exists in GCP org
- [ ] Project `colt-sbx-infra-001` is active
- [ ] Backend bucket `build_logs_001` created
- [ ] Service account `bootstrap-sa` exists
- [ ] WIF service connection verified successfully
- [ ] Folder IAM viewer role applied
- [ ] Bootstrap pipeline ran successfully
- [ ] Sandbox pipeline deployed all resources
- [ ] Can see resources in GCP Console
- [ ] Temporary service account deleted

**All checked?** 🎉 **Infrastructure is ready!**

---

**Congratulations!** You've set up automated GCP infrastructure deployment with Azure DevOps! 🚀
