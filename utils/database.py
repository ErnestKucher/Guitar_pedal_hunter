import sqlite3
from pathlib import Path
from datetime import date, timedelta

DB_FILE = Path("data/pedal_hunter.db")

def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
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
                listing_type TEXT,
                scraped_at TEXT,
                source TEXT
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_sold_once
            ON price_history (search_query, listing_id, source)
            WHERE listing_type = 'sold'
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_active_daily
            ON price_history (search_query, listing_id, scraped_at, source)
            WHERE listing_type = 'active'
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

def save_seen_deals(listing_id, title, price, url, condition, found_at):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO seen_deals (id, title, price, url, condition, found_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (listing_id, title, price, url, condition, found_at))

def prune_seen_deals(max_age_days=30):
    cutoff_date = date.today() - timedelta(days=max_age_days)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM seen_deals WHERE found_at < ?", (cutoff_date.isoformat(),))

def save_price_history(search_query, listing_id, listing_title, listing_price, listing_condition, listing_url, listing_type, source):
    scraped_at = date.today().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO price_history (search_query, listing_id, listing_title, listing_price, listing_condition, listing_url, listing_type, scraped_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (search_query, listing_id, listing_title, listing_price, listing_condition, listing_url, listing_type, scraped_at, source))

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully")