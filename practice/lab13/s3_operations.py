"""
Lab 13 - Task 3: S3 Operations via boto3.

Performs: upload with metadata, download, paginated list, presigned URL, delete.
Configure BUCKET and OWNER below (or export env vars LAB_BUCKET, LAB_OWNER).
"""

import csv
import os
import sys

import boto3
from botocore.exceptions import ClientError

BUCKET = os.environ.get("LAB_BUCKET", "alexanderd-data-lake-lab-2026")
OWNER = os.environ.get("LAB_OWNER", "alexanderd")
REGION = os.environ.get("AWS_REGION", "eu-north-1")

KEY = "uploads/report.csv"
LOCAL_SOURCE = "report.csv"
LOCAL_DOWNLOAD = "downloaded_report.csv"
PRESIGN_TTL_SECONDS = 7200


def make_sample_csv(path: str) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "department", "revenue"])
        writer.writerow([1, "analytics", 15000])
        writer.writerow([2, "sales", 23000])
        writer.writerow([3, "engineering", 41000])


def main() -> int:
    # 1. Create S3 client
    s3 = boto3.client("s3", region_name=REGION)

    # 2-3. Create sample file and upload with custom metadata
    make_sample_csv(LOCAL_SOURCE)
    s3.upload_file(
        LOCAL_SOURCE,
        BUCKET,
        KEY,
        ExtraArgs={"Metadata": {"department": "analytics", "owner": OWNER}},
    )
    print(f"[1/5] Uploaded s3://{BUCKET}/{KEY} with metadata")

    # 4. Download back under a different local name
    s3.download_file(BUCKET, KEY, LOCAL_DOWNLOAD)
    print(f"[2/5] Downloaded to ./{LOCAL_DOWNLOAD}")

    # 5. Paginated listing of uploads/ prefix
    print(f"[3/5] Objects in s3://{BUCKET}/uploads/ :")
    paginator = s3.get_paginator("list_objects_v2")
    total = 0
    for page in paginator.paginate(Bucket=BUCKET, Prefix="uploads/"):
        for obj in page.get("Contents", []):
            print(f"      {obj['Key']:40s} {obj['Size']:>8} B   {obj['LastModified']}")
            total += 1
    print(f"      ({total} object(s) total)")

    # 6. Presigned URL valid for 2 hours
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": KEY},
        ExpiresIn=PRESIGN_TTL_SECONDS,
    )
    print(f"[4/5] Presigned URL (valid {PRESIGN_TTL_SECONDS // 3600} h):\n      {url}")

    # 7. Verify existence via head_object, then delete
    try:
        head = s3.head_object(Bucket=BUCKET, Key=KEY)
        print(
            f"[5/5] head_object OK: ETag={head['ETag']} "
            f"metadata={head.get('Metadata', {})}"
        )
        s3.delete_object(Bucket=BUCKET, Key=KEY)
        print(f"      Deleted s3://{BUCKET}/{KEY}")
    except ClientError as exc:
        print(f"      head_object failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
