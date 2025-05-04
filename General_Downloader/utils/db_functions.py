import hashlib
import sqlite3
from pathlib import Path

def fetch_all_from_db(db_path: str, table: str = "images") -> tuple[list[str], list[tuple]]:
    """Fetch all rows and column names from the given table in the database."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            headers = [description[0] for description in cursor.description]
    except Exception as e:
        print(f"❌ Failed to fetch data from {db_path}: {e}\n")
        return [], []  # Return empty lists on error
    return headers, rows