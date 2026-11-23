"""
Step 3 - Run every query in sql/analysis_queries.sql against the cleaned data.

Loads data/processed/customers_clean.csv into a local SQLite database, runs
each "-- name:" query and saves the result to results/<name>.csv.
(The same SQL also runs in MySQL after loading the CSV with sql/schema.sql.)

Usage:  python scripts/run_sql_analysis.py
"""

import os
import re
import sqlite3

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CLEAN = os.path.join(ROOT, "data", "processed", "customers_clean.csv")
SQL_FILE = os.path.join(ROOT, "sql", "analysis_queries.sql")
RESULTS = os.path.join(ROOT, "results")


def load_queries(path: str) -> dict:
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.MULTILINE)
    # parts = [header, name1, sql1, name2, sql2, ...]
    return {parts[i]: parts[i + 1].strip().rstrip(";") for i in range(1, len(parts), 2)}


def main():
    os.makedirs(RESULTS, exist_ok=True)
    conn = sqlite3.connect(":memory:")
    pd.read_csv(CLEAN).to_sql("customers", conn, index=False)

    pd.set_option("display.width", 140)
    for name, query in load_queries(SQL_FILE).items():
        result = pd.read_sql_query(query, conn)
        result.to_csv(os.path.join(RESULTS, f"{name}.csv"), index=False)
        print(f"\n=== {name} ===")
        print(result.to_string(index=False))
    conn.close()
    print(f"\nSaved results to {os.path.normpath(RESULTS)}")


if __name__ == "__main__":
    main()
