# 1. Define Variables
export PROJECT_ID="cloud-practice-dev-2"
export POOL_NAME="github-pool"
export PROVIDER_NAME="github-provider"
export SA_EMAIL="your-terraform-sa@cloud-practice-dev-2.iam.gserviceaccount.com" # The SA you use for Terraform
export REPO="YOUR_GITHUB_USERNAME/YOUR_REPO_NAME" # e.g., "johndoe/terraform-infra"

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

# 4. Allow GitHub Actions to impersonate your Service Account
# This grants access ONLY to the 'main' branch of your specific repo
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$REPO"

# 5. Get the Provider Resource Name (You need this for the Secret)
gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --format="value(name)"



  Step 2: Add Secrets to GitHub
Go to your GitHub Repository.
Navigate to Settings > Secrets and variables > Actions.
Click New repository secret.
Add the following two secrets:
Secret Name	Value
WIF_PROVIDER	The output from command #5 above (e.g., projects/12345/locations/global/...)
WIF_SERVICE_ACCOUNT	Your Service Account email (e.g., terraform@cloud-practice-dev-2...)
Step 3: Verify Environment Variables
In your 
terraform.yaml
 file, I already added:

yaml
env:
  GCS_LOG_BUCKET: build_logs_001
