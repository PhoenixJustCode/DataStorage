"""
ETL Pipeline: Extract data from Random User Generator API,
transform it, and load into SQLite database.
"""

import logging
import sqlite3
import traceback
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logger = logging.getLogger("etl_pipeline")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    "etl_pipeline.log", maxBytes=1_000_000, backupCount=3
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

API_URL = "https://randomuser.me/api/?results=20"
DEFAULT_DB = "users.db"


# ---------------------------------------------------------------------------
# Task 1: Extract
# ---------------------------------------------------------------------------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)
def _fetch_api():
    """Fetch 20 random users from the API with retry logic."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def extract(existing_emails=None):
    """
    Extract users from the Random User API.

    Parameters
    ----------
    existing_emails : set or None
        A set of emails already present in the database.
        New users whose email is in this set will be filtered out.

    Returns
    -------
    pd.DataFrame
        Raw user data.
    """
    logger.info("Extract: started")
    data = _fetch_api()
    users = data.get("results", [])
    df = pd.DataFrame(users)
    logger.info("Extract: fetched %d users from API", len(df))

    if existing_emails:
        before = len(df)
        df = df[~df["email"].isin(existing_emails)]
        filtered = before - len(df)
        if filtered:
            logger.info("Extract: filtered out %d already-loaded users", filtered)

    logger.info("Extract: finished with %d new users", len(df))
    return df


# ---------------------------------------------------------------------------
# Task 2: Transform
# ---------------------------------------------------------------------------
def transform(df):
    """
    Transform raw user DataFrame:
    - Flatten name -> first_name, last_name
    - Flatten dob -> age, dob_date
    - Add age_group, email_domain, loaded_at
    - Remove duplicates and rows with missing email
    """
    logger.info("Transform: started with %d rows", len(df))

    if df.empty:
        logger.info("Transform: empty DataFrame, returning as-is")
        return pd.DataFrame(columns=[
            "email", "gender", "first_name", "last_name", "nationality",
            "age", "age_group", "email_domain", "dob_date", "loaded_at",
        ])

    result = pd.DataFrame()
    result["email"] = df["email"]
    result["gender"] = df["gender"]

    # Flatten name
    name_df = pd.json_normalize(df["name"])
    result["first_name"] = name_df["first"].values
    result["last_name"] = name_df["last"].values

    # Nationality
    result["nationality"] = df["nat"]

    # Flatten dob
    dob_df = pd.json_normalize(df["dob"])
    result["age"] = dob_df["age"].astype(int).values
    result["dob_date"] = dob_df["date"].values

    # Age group (vectorized with pd.cut)
    bins = [-1, 17, 30, 60, 200]
    labels = ["Child", "Young Adult", "Adult", "Senior"]
    result["age_group"] = pd.cut(result["age"], bins=bins, labels=labels)

    # Email domain
    result["email_domain"] = result["email"].str.split("@").str[1]

    # Loaded at
    result["loaded_at"] = datetime.now(timezone.utc).isoformat()

    # Drop rows with missing email
    missing = result["email"].isna().sum()
    if missing:
        logger.warning("Transform: dropping %d rows with missing email", missing)
    result = result.dropna(subset=["email"])

    # Remove duplicate emails
    dupes = result.duplicated(subset=["email"], keep="first").sum()
    if dupes:
        logger.warning("Transform: dropping %d duplicate emails", dupes)
    result = result.drop_duplicates(subset=["email"], keep="first")

    logger.info("Transform: finished with %d rows", len(result))
    return result


# ---------------------------------------------------------------------------
# Task 3: Load
# ---------------------------------------------------------------------------
def load(df, db_path=DEFAULT_DB):
    """
    Load transformed DataFrame into SQLite database.
    Returns the number of new rows inserted.
    """
    logger.info("Load: started with %d rows", len(df))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            gender TEXT,
            first_name TEXT,
            last_name TEXT,
            nationality TEXT,
            age INTEGER,
            age_group TEXT,
            email_domain TEXT,
            dob_date TEXT,
            loaded_at TEXT
        )
    """)

    if df.empty:
        conn.close()
        logger.info("Load: no rows to insert")
        return 0

    rows = df[["email", "gender", "first_name", "last_name", "nationality",
               "age", "age_group", "email_domain", "dob_date", "loaded_at"]].values.tolist()

    cursor.executemany(
        "INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    loaded_count = cursor.rowcount
    conn.commit()
    conn.close()

    logger.info("Load: inserted %d new rows", loaded_count)
    return loaded_count


# ---------------------------------------------------------------------------
# Task 4: Incremental Control
# ---------------------------------------------------------------------------
def _ensure_control_table(db_path=DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS etl_control (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_last_email(db_path=DEFAULT_DB):
    """Return the most recent email loaded, or None if first run."""
    _ensure_control_table(db_path)
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT value FROM etl_control WHERE key = 'last_email'"
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_existing_emails(db_path=DEFAULT_DB):
    """Return a set of all emails currently in the users table."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT email FROM users").fetchall()
        return {r[0] for r in rows}
    except sqlite3.OperationalError:
        return set()
    finally:
        conn.close()


def update_last_email(last_email, db_path=DEFAULT_DB):
    """Store the maximum email (lexicographically) from the current batch."""
    _ensure_control_table(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO etl_control (key, value) VALUES ('last_email', ?)",
        (last_email,),
    )
    conn.commit()
    conn.close()
    logger.info("Incremental control: updated last_email to %s", last_email)


# ---------------------------------------------------------------------------
# Task 6: Main pipeline with error handling & alerting
# ---------------------------------------------------------------------------
def run_etl(db_path=DEFAULT_DB):
    """Run the full ETL pipeline."""
    try:
        logger.info("=" * 50)
        logger.info("ETL pipeline run started")

        # Incremental: get existing emails
        existing = get_existing_emails(db_path)
        logger.info("Found %d existing emails in database", len(existing))

        # Extract
        raw_df = extract(existing_emails=existing if existing else None)

        # Transform
        transformed_df = transform(raw_df)

        # Load
        loaded = load(transformed_df, db_path)

        # Update control
        if not transformed_df.empty:
            max_email = transformed_df["email"].max()
            update_last_email(max_email, db_path)

        logger.info("ETL pipeline run completed: %d rows loaded", loaded)
        logger.info("=" * 50)
        return loaded

    except Exception as e:
        logger.error("ETL pipeline failed: %s\n%s", e, traceback.format_exc())
        # Simulate Slack alert by writing to alert.log
        with open("alert.log", "a") as f:
            f.write(
                f"[{datetime.now(timezone.utc).isoformat()}] ALERT: ETL pipeline failed — {e}\n"
            )
        raise


if __name__ == "__main__":
    run_etl()
