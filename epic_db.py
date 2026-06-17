import sqlite3
from typing import List, Dict, Any

DB_PATH = "epic_games.db"

def init_epic_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS epic_games (
            game_id TEXT PRIMARY KEY,
            name TEXT,
            header_url TEXT,
            sandbox TEXT,
            last_updated INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS epic_auth (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_epic_games() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT game_id, name, header_url FROM epic_games ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"game_id": row[0], "name": row[1], "image_url": row[2]} for row in rows]

def upsert_epic_game(game_id: str, name: str, header_url: str, sandbox: str, last_updated: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO epic_games (game_id, name, header_url, sandbox, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (game_id, name, header_url, sandbox, last_updated))
    conn.commit()
    conn.close()

def clear_epic_games():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM epic_games")
    conn.commit()
    conn.close()

def save_epic_auth(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO epic_auth (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_epic_auth(key: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM epic_auth WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None