import sqlite3
import os
import sys
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "database.db")

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(drop_existing: bool = False):
    if not os.path.exists(DB_PATH):
        conn = connect_db()
        c = conn.cursor()

        if drop_existing:
            c.execute("DROP TABLE IF EXISTS rewards")
            c.execute("DROP TABLE IF EXISTS progress_tracking")
            c.execute("DROP TABLE IF EXISTS login_info")
            conn.commit()

        c.execute('''
        CREATE TABLE IF NOT EXISTS login_info (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT UNIQUE NOT NULL,
            password       TEXT NOT NULL,
            sync_pending   INTEGER DEFAULT 1,
            last_modified  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT NOT NULL,
            game_name      TEXT NOT NULL,
            best_level     INTEGER NOT NULL DEFAULT 0,
            best_time      REAL,
            mistakes       INTEGER NOT NULL DEFAULT 0,
            last_played    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sync_pending   INTEGER NOT NULL DEFAULT 1,
            last_modified  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, game_name),
            FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS rewards (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT NOT NULL,
            sticker_name   TEXT NOT NULL,
            unlocked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sync_pending   INTEGER NOT NULL DEFAULT 1,
            last_modified  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, sticker_name),
            FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
        )
        ''')

        conn.commit()
        conn.close()

def ensure_user(username: str, password: str = "") -> int:
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO login_info(username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    c.execute("SELECT id FROM login_info WHERE username = ?", (username,))
    user_id = c.fetchone()[0]
    conn.close()
    return user_id

def upsert_progress(username: str, game_name: str, best_level: int, best_time: float = None, mistakes: int = 0):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO progress_tracking(
            username, game_name, best_level, best_time, mistakes
        ) VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username, game_name) DO UPDATE SET
            best_level    = excluded.best_level,
            best_time     = excluded.best_time,
            mistakes      = excluded.mistakes,
            last_played   = CURRENT_TIMESTAMP,
            sync_pending  = 1,
            last_modified = CURRENT_TIMESTAMP
    ''', (username, game_name, best_level, best_time, mistakes))
    conn.commit()
    conn.close()

def unlock_sticker(username: str, sticker_name: str) -> None:
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO rewards(username, sticker_name) VALUES (?, ?) "
        "ON CONFLICT(username, sticker_name) DO NOTHING",
        (username, sticker_name)
    )
    conn.commit()
    conn.close()

def get_progress(username: str, game_name: str) -> dict:
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        SELECT best_level, best_time, mistakes, last_played
        FROM progress_tracking
        WHERE username = ? AND game_name = ?
    ''', (username, game_name))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'best_level': row[0],
            'best_time': row[1],
            'mistakes': row[2],
            'last_played': row[3]
        }
    return {'best_level': 0, 'best_time': None, 'mistakes': 0, 'last_played': None}

def get_unlocked_stickers(username: str) -> list[str]:
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT sticker_name FROM rewards WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

if __name__ == '__main__':
    init_db(drop_existing=False)
