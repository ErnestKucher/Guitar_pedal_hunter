import sqlite3
from pathlib import Path

DB_FILE = Path("data/pedal_hunter.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def create_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_deals (
                id TEXT PRIMARY KEY,
                title TEXT,
                price REAL,
                url TEXT,
                condition TEXT,
                found_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT,
                listing_id TEXT,
                listing_title TEXT,
                listing_price REAL,
                listing_condition TEXT,
                listing_url TEXT,
                scraped_at TEXT
            )
        """)

def load_seen():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, price, url, condition, found_at FROM seen_deals")
        rows = cursor.fetchall()
        seen = {}
        for row in rows:
            listing_id, title, price, url, condition, found_at = row
            seen[listing_id] = {"title": title, "price": price, "url": url, "condition": condition, "found_at": found_at}
        return seen

