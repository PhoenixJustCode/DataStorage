#!/usr/bin/env bash
# Lab 13 - Post-lab cleanup: empty versioned bucket + delete it.
# Usage:  BUCKET=your-bucket-name bash cleanup.sh
# WARNING: destroys all objects, versions and delete markers in the bucket.
set -euo pipefail

BUCKET="${BUCKET:-alexanderd-data-lake-lab-2026}"
REGION="${REGION:-eu-north-1}"

echo "About to delete EVERYTHING in s3://${BUCKET} and the bucket itself."
read -r -p "Type the bucket name to confirm: " CONFIRM
if [[ "${CONFIRM}" != "${BUCKET}" ]]; then
  echo "Aborted."
  exit 1
fi

echo "Deleting current objects ..."
aws s3 rm "s3://${BUCKET}" --recursive || true

echo "Deleting all object versions ..."
VERSIONS=$(aws s3api list-object-versions --bucket "${BUCKET}" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json)
if [[ "${VERSIONS}" != *'"Objects": null'* && "${VERSIONS}" != '{"Objects":null}' ]]; then
  aws s3api delete-objects --bucket "${BUCKET}" --delete "${VERSIONS}" || true
fi

echo "Deleting all delete markers ..."
MARKERS=$(aws s3api list-object-versions --bucket "${BUCKET}" \
  --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
  --output json)
if [[ "${MARKERS}" != *'"Objects": null'* && "${MARKERS}" != '{"Objects":null}' ]]; then
  aws s3api delete-objects --bucket "${BUCKET}" --delete "${MARKERS}" || true
fi

echo "Deleting bucket ..."
aws s3api delete-bucket --bucket "${BUCKET}" --region "${REGION}"

echo "Done. Local artefacts to remove manually (if any):"
echo "  test.txt sample.csv report.csv downloaded_report.csv downloaded/"
