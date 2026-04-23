#!/usr/bin/env bash
# Lab 13 - Task 2: AWS CLI upload / list / download.
# Usage:  BUCKET=your-bucket-name bash task2_cli_commands.sh
set -euo pipefail

BUCKET="${BUCKET:-alexanderd-data-lake-lab-2026}"

echo "=== 1. Create local test.txt ==="
echo "Hello Cloud Storage!" > test.txt
cat test.txt

echo
echo "=== 2. Upload test.txt -> data/test.txt ==="
aws s3 cp test.txt "s3://${BUCKET}/data/test.txt"

echo
echo "=== 3. Create sample.csv and upload -> data/sample.csv ==="
cat > sample.csv <<'CSV'
id,name,value
1,alpha,100
2,beta,200
3,gamma,300
CSV
aws s3 cp sample.csv "s3://${BUCKET}/data/sample.csv"

echo
echo "=== 4. List objects under data/ ==="
aws s3 ls "s3://${BUCKET}/data/"

echo
echo "=== 5. Download data/ recursively into ./downloaded/ ==="
mkdir -p downloaded
aws s3 cp "s3://${BUCKET}/data/" downloaded/ --recursive
ls -la downloaded/

echo
echo "Done."
