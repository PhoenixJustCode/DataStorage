#!/usr/bin/env bash
# Lab 13 - Task 1: Create bucket with versioning + SSE-S3 + public access block.
# Usage:  BUCKET=your-globally-unique-name bash task1_create_bucket.sh
set -euo pipefail

BUCKET="${BUCKET:-alexanderd-data-lake-lab-2026}"
REGION="${REGION:-eu-north-1}"

echo "Creating bucket s3://${BUCKET} in ${REGION} ..."
aws s3api create-bucket \
  --bucket "${BUCKET}" \
  --region "${REGION}" \
  --create-bucket-configuration "LocationConstraint=${REGION}"

echo "Enabling versioning ..."
aws s3api put-bucket-versioning \
  --bucket "${BUCKET}" \
  --versioning-configuration Status=Enabled

echo "Enabling SSE-S3 default encryption ..."
aws s3api put-bucket-encryption \
  --bucket "${BUCKET}" \
  --server-side-encryption-configuration '{
    "Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]
  }'

echo "Blocking all public access ..."
aws s3api put-public-access-block \
  --bucket "${BUCKET}" \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo
echo "Verification:"
aws s3api get-bucket-versioning --bucket "${BUCKET}"
aws s3api get-bucket-encryption --bucket "${BUCKET}"
aws s3api get-public-access-block --bucket "${BUCKET}"
