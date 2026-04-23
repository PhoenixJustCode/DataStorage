#!/usr/bin/env bash
# Lab 13 - Task 4: Apply lifecycle policy from task4_lifecycle.json.
# Usage:  BUCKET=your-bucket-name bash task4_apply_lifecycle.sh
set -euo pipefail

BUCKET="${BUCKET:-alexanderd-data-lake-lab-2026}"

aws s3api put-bucket-lifecycle-configuration \
  --bucket "${BUCKET}" \
  --lifecycle-configuration "file://task4_lifecycle.json"

echo "Applied. Current configuration:"
aws s3api get-bucket-lifecycle-configuration --bucket "${BUCKET}"
