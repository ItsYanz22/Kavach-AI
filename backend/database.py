import os
import sqlite3
from datetime import datetime

# Always store the db next to this file, not relative to cwd
_db_path = os.path.join(os.path.dirname(__file__), "kavach.db")

conn = sqlite3.connect(_db_path, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scam_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    classification TEXT,
    confidence REAL,
    timestamp TEXT
)
""")
conn.commit()


def log_detection(message: str, classification: str, confidence: float):
    """Insert a detection record."""
    cursor.execute(
        "INSERT INTO scam_logs (message, classification, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (message, classification, confidence, datetime.now().isoformat()),
    )
    conn.commit()


def get_history():
    """Return the 20 most recent detection records."""
    cursor.execute("SELECT * FROM scam_logs ORDER BY id DESC LIMIT 20")
    return cursor.fetchall()