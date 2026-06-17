import sqlite3
from typing import List, Dict, Any

DB_PATH = "cubejoy_games.db"

def init_cubejoy_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cubejoy_games (
            game_id TEXT PRIMARY KEY,
            s_id TEXT,
            name TEXT,
            image_url TEXT,
            last_updated INTEGER
        )
    ''')
    # 兼容旧表，添加 s_id 列
    c.execute("PRAGMA table_info(cubejoy_games)")
    columns = [col[1] for col in c.fetchall()]
    if 's_id' not in columns:
        c.execute("ALTER TABLE cubejoy_games ADD COLUMN s_id TEXT")
    conn.commit()
    conn.close()

def get_all_cubejoy_games() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT game_id, s_id, name, image_url FROM cubejoy_games ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"game_id": row[0], "s_id": row[1] or '', "name": row[2], "image_url": row[3]} for row in rows]

def upsert_cubejoy_game(game_id: str, s_id: str, name: str, image_url: str, last_updated: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO cubejoy_games (game_id, s_id, name, image_url, last_updated)
        VALUES (?, ?, ?, ?, ?)
    ''', (game_id, s_id, name, image_url, last_updated))
    conn.commit()
    conn.close()

def clear_cubejoy_games():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cubejoy_games")
    conn.commit()
    conn.close()

def count_cubejoy_games() -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cubejoy_games")
    count = c.fetchone()[0]
    conn.close()
    return count