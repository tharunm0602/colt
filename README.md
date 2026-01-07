# GCP Cloud Build Terraform CI/CD Setup

This guide explains how to set up the Google Cloud Build pipeline for automated Terraform checks (Format, Security, Lint, and Plan).

---

## � Step 1: Connect GitHub to GCP
Before creating a trigger, you must link your GitHub repository to your GCP project.

1. Go to **GCP Console > Cloud Build > Repositories**.
2. Click **Connect Repository**.
3. Select **GitHub (Cloud Build GitHub App)**.
4. Authenticate with GitHub and select your repository (`tharunm0602/colt`).
5. Click **Connect**.

---

## ⚡ Step 2: Create the Cloud Build Trigger
1. Go to **GCP Console > Cloud Build > Triggers**.
2. Click **Create Trigger**.
3. **Name**: `terraform-ci-cd`
4. **Event**: Select **Push to a branch**.
5. **Source**:
   - **Repository**: Select your connected repo.
   - **Branch**: `^main$`
6. **Configuration**:
   - **Type**: **Cloud Build configuration file (yaml or json)**.
   - **Location**: `cloudbuild.yaml` (ensure it is in the root of your repo).
7. **Approval (Optional but Recommended)**:
   - Toggle **"Require approval before build can run"** to **ON**.
8. **Substitutions**: (See Step 3 below).

---

## 🔑 Step 3: Configure Authentication (Choose One Method)

### Option A: Using Trigger Substitutions (Easiest)
Use this if you do not have permissions for Secret Manager.

1. In your Trigger settings, scroll to **Substitutions**.
2. Add:
   - **Variable**: `_GITHUB_TOKEN`
   - **Value**: Your GitHub PAT (Personal Access Token).
3. Ensure your `cloudbuild.yaml` uses `${_GITHUB_TOKEN}` in the fetch step.

### Option B: Using Secret Manager (Most Secure)
Use this for production environments.

1. **Create the Secret**:
   ```bash
   echo "your_github_pat_here" | gcloud secrets create github-token --data-file=-
   ```
2. **Grant Permissions**:
   ```bash
   export PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
   gcloud secrets add-iam-policy-binding github-token \
       --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```
3. **Update YAML**: Add the `availableSecrets` block at the bottom of `cloudbuild.yaml`.

---

## 📝 Pipeline Overview
The pipeline executes the following for every changed directory:

1. **Fetch**: Downloads git history to detect changes.
2. **Detect**: Identifies folders with `.tf` or `.tfvars` modifications.
3. **Checks**:
   - `terraform fmt`: Validates code formatting.
   - `trivy`: Scans for security vulnerabilities.
   - `tflint`: Checks for cloud-specific best practices.
   - `terraform init/plan`: Generates the execution plan.
4. **Logging**: Captures all output into a single file and uploads it to:
   `gs://build_logs_001/cloud-build/terraform_plan_<BUILD_ID>.log`
