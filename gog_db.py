import sqlite3
from typing import List, Dict, Any

DB_PATH = "gog_games.db"

def init_gog_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gog_games (
            game_id TEXT PRIMARY KEY,
            name TEXT,
            image_url TEXT,
            last_updated INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_all_gog_games() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT game_id, name, image_url FROM gog_games ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"game_id": row[0], "name": row[1], "image_url": row[2]} for row in rows]

def upsert_gog_game(game_id: str, name: str, image_url: str, last_updated: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO gog_games (game_id, name, image_url, last_updated)
        VALUES (?, ?, ?, ?)
    ''', (game_id, name, image_url, last_updated))
    conn.commit()
    conn.close()

def clear_gog_games():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM gog_games")
    conn.commit()
    conn.close()

def count_gog_games() -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM gog_games")
    count = c.fetchone()[0]
    conn.close()
    return count