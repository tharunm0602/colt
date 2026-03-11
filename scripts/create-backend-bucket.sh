#!/bin/bash
set -e

# Script to create GCS backend bucket for Terraform state
# This should be run before any Terraform operations

echo "======================================"
echo "Creating GCS Backend Bucket"
echo "======================================"

# Configuration
BUCKET_NAME="build_logs_001"
PROJECT_ID="${GCP_PROJECT_ID:-colt-sbx-infra-001}"
REGION="${GCP_REGION:-us-central1}"

echo "Bucket Name: ${BUCKET_NAME}"
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Check if bucket already exists
if gsutil ls -b gs://${BUCKET_NAME} 2>/dev/null; then
  echo "✅ Bucket ${BUCKET_NAME} already exists. Skipping creation."
else
  echo "Creating bucket ${BUCKET_NAME}..."
  
  # Create bucket with versioning and uniform bucket-level access
  gcloud storage buckets create gs://${BUCKET_NAME} \
    --project=${PROJECT_ID} \
    --location=${REGION} \
    --uniform-bucket-level-access \
    --public-access-prevention=enforced
  
  # Enable versioning
  gsutil versioning set on gs://${BUCKET_NAME}
  
  echo "✅ Bucket ${BUCKET_NAME} created successfully"
fi

echo ""
echo "======================================"
echo "Backend bucket is ready!"
echo "======================================"
