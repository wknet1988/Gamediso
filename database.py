import sqlite3
import json
from typing import List, Dict, Any

DB_PATH = "steam_games.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 游戏表
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            appid INTEGER PRIMARY KEY,
            name TEXT,
            header_url TEXT,
            last_updated INTEGER
        )
    ''')
    # 货架表（从 Steam 读取的分组）
    c.execute('''
        CREATE TABLE IF NOT EXISTS shelves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            type TEXT   -- 'favorite' or 'custom'
        )
    ''')
    # 货架-游戏关联表
    c.execute('''
        CREATE TABLE IF NOT EXISTS shelf_games (
            shelf_id INTEGER,
            appid INTEGER,
            position INTEGER,
            PRIMARY KEY (shelf_id, appid)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            appid INTEGER PRIMARY KEY,
            name TEXT,
            header_url TEXT,
            last_updated INTEGER,
            type TEXT DEFAULT 'owned'
        )
    ''')
    # 如果已存在表但没有 type 列，则添加
    c.execute("PRAGMA table_info(games)")
    columns = [col[1] for col in c.fetchall()]
    if 'type' not in columns:
        c.execute("ALTER TABLE games ADD COLUMN type TEXT DEFAULT 'owned'")

    conn.commit()
    conn.close()

def get_all_games() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT appid, name, header_url, type FROM games ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"appid": row[0], "name": row[1], "image_url": row[2], "type": row[3]} for row in rows]

def upsert_game(appid: int, name: str, header_url: str, last_updated: int, game_type: str = 'owned'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO games (appid, name, header_url, last_updated, type)
        VALUES (?, ?, ?, ?, ?)
    ''', (appid, name, header_url, last_updated, game_type))
    conn.commit()
    conn.close()

def clear_shelves():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM shelf_games")
    c.execute("DELETE FROM shelves")
    conn.commit()
    conn.close()

def add_shelf(name: str, shelf_type: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO shelves (name, type) VALUES (?, ?)", (name, shelf_type))
    shelf_id = c.lastrowid
    conn.commit()
    conn.close()
    return shelf_id

def add_game_to_shelf(shelf_id: int, appid: int, position: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO shelf_games (shelf_id, appid, position)
        VALUES (?, ?, ?)
    ''', (shelf_id, appid, position))
    conn.commit()
    conn.close()

def get_shelves() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, type FROM shelves ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "type": row[2]} for row in rows]

def get_shelf_games(shelf_id: int) -> List[int]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT appid FROM shelf_games WHERE shelf_id = ? ORDER BY position", (shelf_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]