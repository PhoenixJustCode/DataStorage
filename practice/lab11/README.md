# Lab 11 — ETL Pipeline

ETL pipeline that extracts random user data from the [Random User Generator API](https://randomuser.me/api/), transforms it, and loads it into a SQLite database.

## Setup

```bash
pip install -r requirements.txt
```

## Run the pipeline (single execution)

```bash
python etl_pipeline.py
```

This will:
- Fetch 20 random users from the API
- Transform and clean the data
- Load new rows into `users.db`
- Log activity to `etl_pipeline.log`

## Run the scheduler (6 runs, every 10 minutes)

```bash
python scheduler.py
```

## Run unit tests

```bash
pytest test_transform.py -v
```

## Files

| File | Description |
|---|---|
| `etl_pipeline.py` | Main ETL code (extract, transform, load, logging, error handling) |
| `scheduler.py` | Scheduling script — runs the pipeline every 10 min for 1 hour |
| `test_transform.py` | Pytest unit tests for the `transform()` function |
| `requirements.txt` | Python dependencies |

## Docker

```bash
docker build -t etl-pipeline .
docker run --rm etl-pipeline
```