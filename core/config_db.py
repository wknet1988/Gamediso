import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "config.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

def init_config_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_config_value(key: str) -> str:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_config_value(key: str, value: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_all_config() -> dict:
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM config")
    rows = c.fetchall()
    conn.close()
    return {row[0]: json.loads(row[1]) for row in rows}

def set_all_config(data: dict):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM config")
    for key, value in data.items():
        c.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()