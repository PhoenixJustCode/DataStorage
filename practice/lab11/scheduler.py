"""
Scheduler: Runs the ETL pipeline every 10 minutes for one hour (6 runs).
"""

import time
from datetime import datetime

from DataStorage.practice.lab11.etl_pipeline import run_etl

INTERVAL_SECONDS = 10 * 60  # 10 minutes
TOTAL_RUNS = 6


def main():
    for i in range(1, TOTAL_RUNS + 1):
        print(f"[Run {i}/{TOTAL_RUNS}] Running ETL at {datetime.now().isoformat()} ...")
        try:
            loaded = run_etl()
            print(f"[Run {i}/{TOTAL_RUNS}] Completed — {loaded} rows loaded.")
        except Exception as e:
            print(f"[Run {i}/{TOTAL_RUNS}] Failed — {e}")

        if i < TOTAL_RUNS:
            print(f"Sleeping {INTERVAL_SECONDS // 60} minutes until next run...\n")
            time.sleep(INTERVAL_SECONDS)

    print("Scheduler finished: all 6 runs completed.")


if __name__ == "__main__":
    main()
