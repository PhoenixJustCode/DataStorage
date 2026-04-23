# Lab 13 — AWS S3 Cloud Storage Basics

Hands-on lab for AWS S3: bucket with versioning & encryption, CLI uploads,
`boto3` operations, and a lifecycle policy.

## Files

| File | Purpose |
|---|---|
| `task1_create_bucket.sh` | Creates the bucket with versioning, SSE-S3, public-access block |
| `task2_cli_commands.sh` | Task 2: CLI upload / list / download |
| `s3_operations.py` | Task 3: Python `boto3` script (upload, metadata, download, list, presign, delete) |
| `task4_lifecycle.json` | Lifecycle rule: `archive/` → Standard-IA (30d) → Glacier (90d) → expire (365d) |
| `task4_apply_lifecycle.sh` | Applies the lifecycle policy |
| `cleanup.sh` | Empties the versioned bucket and deletes it (run at the end!) |
| `ans.md` | Russian cheat-sheet for the lesson |

## Prerequisites

1. **AWS account** (Free Tier is enough).
2. **AWS CLI v2** installed — <https://aws.amazon.com/cli/> or `pip install awscli`.
3. **Python 3.9+** and `boto3`:
   ```bash
   pip install boto3
   ```
4. **IAM user with programmatic access.** In the AWS Console:
   `IAM → Users → Create user → Attach policy AmazonS3FullAccess →
   Security credentials → Create access key`.
5. **Configure credentials** locally:
   ```bash
   aws configure
   # AWS Access Key ID:     <paste>
   # AWS Secret Access Key: <paste>
   # Default region name:   eu-north-1
   # Default output format: json
   ```
6. Verify:
   ```bash
   aws sts get-caller-identity
   ```

> Never commit `~/.aws/credentials` to Git.

## Choose a bucket name

S3 bucket names are **globally unique**. Pick something like
`<your-initials>-data-lake-lab-<YYYYMMDD>` and export it once per terminal:

```bash
export BUCKET=alexanderd-data-lake-lab-2026
export REGION=eu-north-1
```

All scripts below read `$BUCKET` (and `$REGION` where relevant). On Windows
PowerShell use `$env:BUCKET="..."`; on `cmd.exe` use `set BUCKET=...`.

## How to run

### Task 1 — Create the bucket

```bash
BUCKET=$BUCKET bash task1_create_bucket.sh
```

Or do it in the AWS Console:
`S3 → Create bucket → Region eu-north-1 → Enable Versioning → Default
encryption SSE-S3 → Block all public access (default) → Create`.

**Deliverable:** screenshot of bucket *Properties* showing **Versioning: Enabled**.

### Task 2 — AWS CLI upload / download

```bash
BUCKET=$BUCKET bash task2_cli_commands.sh
```

This creates `test.txt` + `sample.csv`, uploads them under `data/`, lists the
prefix, and downloads everything into `./downloaded/`.

**Deliverable:** screenshot of the terminal with commands and their output.

### Task 3 — Python `boto3` script

```bash
LAB_BUCKET=$BUCKET LAB_OWNER=alexanderd python s3_operations.py
```

The script:

1. Creates the `boto3` S3 client.
2. Generates `report.csv` with sample data.
3. Uploads it to `uploads/report.csv` with metadata
   `{"department": "analytics", "owner": "<you>"}`.
4. Downloads it back to `downloaded_report.csv`.
5. Lists everything under `uploads/` using a paginator
   (keys, sizes, last-modified).
6. Prints a presigned URL valid for 2 hours.
7. Verifies the object with `head_object` and deletes it.

**Deliverable:** `s3_operations.py` and a screenshot of the output with the
presigned URL and the object listing.

### Task 4 — Lifecycle policy

```bash
BUCKET=$BUCKET bash task4_apply_lifecycle.sh
```

Or, in the Console:
`Bucket → Management → Lifecycle rules → Create lifecycle rule →
Prefix archive/ → Transitions: Standard-IA after 30 days, Glacier Flexible
Retrieval after 90 days → Expiration: 365 days → Create`.

**Deliverable:** screenshot of the lifecycle rules list in the Console.

## Cleanup (important — do this after grading!)

A versioned bucket keeps every version and every delete marker, and you pay
for them. `s3 rm --recursive` alone is not enough.

```bash
BUCKET=$BUCKET bash cleanup.sh
```

The script asks you to retype the bucket name, then removes current objects,
all versions, all delete markers, and finally deletes the bucket.

Also delete local artefacts:

```bash
rm -f test.txt sample.csv report.csv downloaded_report.csv
rm -rf downloaded/
```

## Troubleshooting

- **`InvalidLocationConstraint`** — the region in `--create-bucket-configuration`
  must match `--region`.
- **`BucketAlreadyExists` / `BucketAlreadyOwnedByYou`** — name is taken
  globally; pick a different one.
- **`AccessDenied`** — the IAM user needs `AmazonS3FullAccess` (or an
  equivalent custom policy) for this lab.
- **`BucketNotEmpty` on delete** — run `cleanup.sh`; versioning is enabled, so
  leftover versions/delete markers block deletion.
- **Presigned URL returns `SignatureDoesNotMatch`** — the clock on the machine
  is skewed, or the URL was generated in a different region than the bucket.

## Notes

- Bucket region is pinned to `eu-north-1` (Stockholm) per the assignment.
- Default encryption uses **SSE-S3** (AES-256 with AWS-managed keys) — free.
- `s3_operations.py` is parameterised via env vars (`LAB_BUCKET`, `LAB_OWNER`,
  `AWS_REGION`) so you don't have to edit the source.
