#!/bin/bash

set -e

# =====================================
# 🔧 REQUIRED VARIABLES (EDIT THESE)
# =====================================

PROJECT_ID=""
PROJECT_NUMBER=""
REGION=""

REPO=""

POOL_NAME=""
PROVIDER_NAME=""

SERVICE_ACCOUNT_NAME=""
SERVICE_ACCOUNT_DISPLAY_NAME=""

BUCKET_NAME=""
ARTIFACT_REPO_NAME=""

# =====================================
# ⚙ Derived Values (Do Not Edit)
# =====================================

SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting project..."
gcloud config set project ${PROJECT_ID}

# =====================================
# 1️⃣ Enable Required APIs
# =====================================

echo "Enabling required APIs..."

gcloud services enable \
    iam.googleapis.com \
    iamcredentials.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

# =====================================
# 2️⃣ Create Service Account
# =====================================

echo "Creating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="${SERVICE_ACCOUNT_DISPLAY_NAME}" || true

# =====================================
# 3️⃣ Create Workload Identity Pool
# =====================================

echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create ${POOL_NAME} \
    --location="global" \
    --display-name="GitHub Actions Pool" || true

# =====================================
# 4️⃣ Create OIDC Provider
# =====================================

echo "Creating OIDC Provider..."

gcloud iam workload-identity-pools providers create-oidc ${PROVIDER_NAME} \
    --location="global" \
    --workload-identity-pool=${POOL_NAME} \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --attribute-condition="attribute.repository == '${REPO}'" \
    --issuer-uri="https://token.actions.githubusercontent.com" || true

# =====================================
# 5️⃣ Bind principalSet to Service Account
# =====================================

echo "Binding Workload Identity permissions..."

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${REPO}"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
    --role="roles/iam.serviceAccountTokenCreator" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${REPO}"

# =====================================
# 6️⃣ Grant Runtime Roles to Service Account
# =====================================

echo "Granting runtime roles to Service Account..."

# Cloud Run deploy
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

# Artifact Registry push
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

# Storage bucket object access (NOT full admin)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectAdmin"

# Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"

# Vertex AI usage
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

# =====================================
# 7️⃣ Create Storage Bucket (Secure)
# =====================================

echo "Creating secure GCS bucket..."

gcloud storage buckets create gs://${BUCKET_NAME} \
    --location=${REGION} \
    --uniform-bucket-level-access \
    --public-access-prevention=enforced || true

# =====================================
# 8️⃣ Create Artifact Registry (Docker)
# =====================================

echo "Creating Artifact Registry..."

gcloud artifacts repositories create ${ARTIFACT_REPO_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repo for GitHub deployments" || true

# =====================================
# 9️⃣ Output Required GitHub Secrets
# =====================================

echo ""
echo "=============================================="
echo "ADD THIS TO GITHUB SECRET: GCP_WORKLOAD_PROVIDER"
echo "=============================================="

gcloud iam workload-identity-pools providers describe ${PROVIDER_NAME} \
    --location="global" \
    --workload-identity-pool=${POOL_NAME} \
    --format="value(name)"

echo ""
echo "=============================================="
echo "ADD THIS TO GITHUB SECRET: GCP_SERVICE_ACCOUNT"
echo "=============================================="
echo "${SA_EMAIL}"

echo ""
echo "✅ Production Setup Complete"
