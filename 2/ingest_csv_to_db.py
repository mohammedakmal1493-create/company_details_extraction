"""
One-time setup script: loads your Company Master Data CSV into a SQLite
database that the website's backend will query, instead of the browser
loading the CSV directly.

Usage:
    python ingest_csv_to_db.py company_master_data.csv companies.db

Handles large files (millions of rows) by reading in chunks rather than
loading the whole CSV into memory at once. Auto-detects which column is
the company name (used for searching) and writes that, plus the column
list and row count, to db_meta.json so app.py knows the schema without
you having to hardcode column names anywhere.
"""

import sys
import sqlite3
import re
import json
import pandas as pd


def sanitize(col):
    col = col.strip()
    col = re.sub(r"[^0-9a-zA-Z_]", "_", col)
    if re.match(r"^[0-9]", col):
        col = "_" + col
    return col or "col"


def guess_name_column(columns):
    pattern = re.compile(r"company|business|name|title", re.I)
    for c in columns:
        if pattern.search(c):
            return c
    return columns[0]


def main():
    if len(sys.argv) < 3:
        print("Usage: python ingest_csv_to_db.py <input.csv> <output.db> [table_name]")
        sys.exit(1)

    csv_path = sys.argv[1]
    db_path = sys.argv[2]
    table = sys.argv[3] if len(sys.argv) > 3 else "companies"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table}")

    chunksize = 50000
    total_rows = 0
    columns = None
    sanitized_map = {}

    print(f"Reading {csv_path} in chunks of {chunksize}...")
    for i, chunk in enumerate(
        pd.read_csv(csv_path, dtype=str, chunksize=chunksize, keep_default_na=False)
    ):
        if columns is None:
            columns = list(chunk.columns)
            sanitized_map = {c: sanitize(c) for c in columns}
            chunk = chunk.rename(columns=sanitized_map)
            col_defs = ", ".join(f'"{sanitized_map[c]}" TEXT' for c in columns)
            cur.execute(f"CREATE TABLE {table} ({col_defs})")
            conn.commit()
        else:
            chunk = chunk.rename(columns=sanitized_map)

        chunk.to_sql(table, conn, if_exists="append", index=False)
        total_rows += len(chunk)
        print(f"  Inserted chunk {i + 1}, total rows so far: {total_rows}")

    if columns is None:
        print("No data found in that CSV.")
        return

    name_col = guess_name_column(list(sanitized_map.values()))
    print(f"Detected name/search column: {name_col}")

    print("Building search index (can take a bit on large files)...")
    cur.execute(
        f'CREATE INDEX IF NOT EXISTS idx_{table}_{name_col} '
        f'ON {table} ("{name_col}" COLLATE NOCASE)'
    )
    conn.commit()
    conn.close()

    meta = {
        "table": table,
        "columns": list(sanitized_map.values()),
        "name_column": name_col,
        "total_rows": total_rows,
    }
    with open("db_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nDone. {total_rows} rows loaded into {db_path}, table '{table}'.")
    print("Wrote db_meta.json so app.py knows the schema.")


if __name__ == "__main__":
    main()
