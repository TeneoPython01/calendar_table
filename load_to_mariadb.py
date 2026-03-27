"""
load_to_mariadb.py

Loads calendar_table_output.csv and docs/col_descriptions.csv into MariaDB.
Tables created:
  - calendar_table  (from calendar_table_output.csv)
  - col_desc        (from docs/col_descriptions.csv)

Requires: mysql-connector-python  (pip install mysql-connector-python)
"""

import csv
import os
import mysql.connector

# ---------------------------------------------------------------------------
# Connection settings
# ---------------------------------------------------------------------------
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "dbapi"
DB_PASS = "your_password_here" # use a real username and password with write permissions
DB_NAME = "adhoc_db"

# ---------------------------------------------------------------------------
# CSV paths (relative to this script)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CALENDAR_CSV = os.path.join(SCRIPT_DIR, "calendar_table_output.csv")
COL_DESC_CSV = os.path.join(SCRIPT_DIR, "docs", "col_descriptions.csv")


def sanitize_col(name: str, idx: int) -> str:
    """Return a safe column name; unnamed first column gets 'row_idx'."""
    name = name.strip()
    if not name:
        return "row_idx"
    # Replace characters that are invalid in MariaDB column names
    return name.replace(" ", "_").replace("-", "_").replace(".", "_")


def read_csv(path: str):
    """Return (columns, rows) where rows is a list of tuples."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        raw_headers = next(reader)
        columns = [sanitize_col(h, i) for i, h in enumerate(raw_headers)]
        rows = []
        for row in reader:
            # Pad short rows; convert empty strings to None
            padded = (row + [""] * len(columns))[: len(columns)]
            rows.append(tuple(v if v != "" else None for v in padded))
    return columns, rows


def build_create_table(table_name: str, columns: list[str]) -> str:
    col_defs = ",\n  ".join(f"`{c}` TEXT" for c in columns)
    return f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n  {col_defs}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"


def load_table(cursor, table_name: str, columns: list[str], rows: list[tuple]):
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    cursor.execute(build_create_table(table_name, columns))

    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(f"`{c}`" for c in columns)
    insert_sql = f"INSERT INTO `{table_name}` ({col_list}) VALUES ({placeholders})"

    batch_size = 500
    for i in range(0, len(rows), batch_size):
        cursor.executemany(insert_sql, rows[i : i + batch_size])

    print(f"  Loaded {len(rows):,} rows into `{table_name}`.")


def main():
    print("Connecting to MariaDB...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
    )
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.execute(f"USE `{DB_NAME}`")
    print(f"Using database: {DB_NAME}")

    # --- calendar_table ---
    print(f"\nReading {CALENDAR_CSV} ...")
    cal_cols, cal_rows = read_csv(CALENDAR_CSV)
    print(f"  {len(cal_cols)} columns, {len(cal_rows):,} rows found.")
    load_table(cursor, "calendar_table", cal_cols, cal_rows)

    # --- col_desc ---
    print(f"\nReading {COL_DESC_CSV} ...")
    desc_cols, desc_rows = read_csv(COL_DESC_CSV)
    print(f"  {len(desc_cols)} columns, {len(desc_rows):,} rows found.")
    load_table(cursor, "col_desc", desc_cols, desc_rows)

    conn.commit()
    cursor.close()
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
