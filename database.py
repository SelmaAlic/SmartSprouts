import sqlite3
import os
from datetime import datetime

# Absolute path to the SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database.db")


def connect_db():
    """
    Open a connection to the SQLite database and enforce foreign keys.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(drop_existing: bool = False):
    """
    Initialize the database schema. If drop_existing=True,
    all tables will be dropped and recreated (use to refresh schema).
    """
    conn = connect_db()
    c = conn.cursor()

    if drop_existing:
        c.execute("DROP TABLE IF EXISTS rewards")
        c.execute("DROP TABLE IF EXISTS progress_tracking")
        c.execute("DROP TABLE IF EXISTS login_info")
        conn.commit()

    # 1) login_info: store users
    c.execute('''
    CREATE TABLE IF NOT EXISTS login_info (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        username       TEXT UNIQUE NOT NULL,
        password       TEXT NOT NULL,
        sync_pending   INTEGER DEFAULT 1,
        last_modified  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2) progress_tracking: track progress per (username, game_name)
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

    # 3) rewards: store unlocked stickers per (username, sticker_name)
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
    """
    Ensure that a user with the given username exists.
    If not, insert it with the provided password (or blank).
    Returns the new or existing user ID.
    """
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO login_info(username, password) VALUES (?, ?)",
              (username, password))
    conn.commit()
    c.execute("SELECT id FROM login_info WHERE username = ?", (username,))
    user_id = c.fetchone()[0]
    conn.close()
    return user_id


def upsert_progress(username: str, game_name: str,
                    best_level: int, best_time: float = None, mistakes: int = 0):
    """
    Insert or update a progress record for the given user and game.
    Uses the UNIQUE(username, game_name) constraint to handle conflicts.
    """
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
    """
    Unlock a sticker for the user; does nothing if already unlocked.
    Uses the UNIQUE(username, sticker_name) constraint for idempotency.
    """
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
    """
    Retrieve progress data for a given user and game.
    Returns a dict with keys: best_level, best_time, mistakes, last_played.
    """
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
    """
    Return a list of sticker_name strings that the user has unlocked.
    """
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT sticker_name FROM rewards WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


if __name__ == '__main__':
    # Reinitialize database schema (drop + create)
    init_db(drop_existing=True)
    print("✅ Database is ready and data displayed successfully.")