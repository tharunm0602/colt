# GCP Terraform CI/CD with GitHub Actions

This repository contains Terraform configurations for managing GCP resources (Workbench, Artifact Registry, VPCs) with a fully automated CI/CD pipeline using GitHub Actions and Google Cloud **Workload Identity Federation (WIF)**.

## 🛠️ Setup Instructions

### 1. Google Cloud Configuration
Run the following commands in your Google Cloud Shell to set up the authentication bridge.

```bash
# 1. Define Variables
export PROJECT_ID="cloud-practice-dev-2"
export POOL_NAME="github-pool"
export PROVIDER_NAME="github-provider"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export SA_EMAIL="terraform-sa@${PROJECT_ID}.iam.gserviceaccount.com"
export REPO="tharunm0602/colt" # Your GitHub username/repository

# 2. Create the Workload Identity Pool
gcloud iam workload-identity-pools create $POOL_NAME \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# 3. Create the Identity Provider
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="attribute.repository == '${REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 4. Allow GitHub Actions to impersonate the Service Account
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${REPO}"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${REPO}"

# 5. Get the Provider Resource Name for GitHub Secrets
gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --format="value(name)"
```

### 2. GitHub Secrets Configuration
Navigate to your GitHub Repository **Settings > Secrets and variables > Actions** and add the following secrets:

| Secret Name | Value |
| :--- | :--- |
| `WIF_PROVIDER` | The output from Step 5 above (e.g., `projects/123456/locations/global/...`) |
| `WIF_SERVICE_ACCOUNT` | Your Service Account email (`terraform-sa@cloud-practice-dev-2.iam.gserviceaccount.com`) |

---



