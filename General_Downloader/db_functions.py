import hashlib
import sqlite3
from pathlib import Path


def get_sha256(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_sha256(db_path, image_path, sha256):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM archive WHERE SHA256 = ?", (sha256,))
            return cur.fetchone() is not None
    except Exception as e:
        print(f"❌ DB check failed: {e}\n")
        return False


def init_db(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    rating TEXT,
                    character_tags TEXT,
                    general_tags TEXT,
                    SHA256 TEXT UNIQUE,
                    model TEXT,
                    score REAL
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"❌ Failed to init {db_path}: {e}\n")


def insert_to_db(db_path, filename, rating, character_tags, general_tags, sha256, model=None, score=None):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO archive 
                (filename, rating, character_tags, general_tags, SHA256, model, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                filename,
                rating if rating else "",
                ", ".join(character_tags),
                ", ".join(general_tags),
                sha256,
                model,
                score,
            ))
            conn.commit()
            print(f"💾 Saved to: {db_path}")
    except Exception as e:
        print(f"❌ Failed to save to {db_path}: {e}\n")

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