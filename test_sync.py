import sqlite3


def init_db(conn):
    c = conn.cursor()
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

def ensure_user(conn, username: str, password: str = "") -> int:
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO login_info(username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    c.execute("SELECT id FROM login_info WHERE username = ?", (username,))
    user_id = c.fetchone()[0]
    return user_id

def upsert_progress(conn, username: str, game_name: str, best_level: int, best_time: float = None, mistakes: int = 0):
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

def unlock_sticker(conn, username: str, sticker_name: str) -> None:
    c = conn.cursor()
    c.execute(
        "INSERT INTO rewards(username, sticker_name) VALUES (?, ?) "
        "ON CONFLICT(username, sticker_name) DO NOTHING",
        (username, sticker_name)
    )
    conn.commit()

def mark_synced(conn):
    c = conn.cursor()
    c.execute("UPDATE login_info SET sync_pending=0 WHERE sync_pending=1")
    c.execute("UPDATE progress_tracking SET sync_pending=0 WHERE sync_pending=1")
    c.execute("UPDATE rewards SET sync_pending=0 WHERE sync_pending=1")
    conn.commit()



def test_sync_function():

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)

    user_id = ensure_user(conn, "alice", "secret")
    upsert_progress(conn, "alice", "math_game", 5, 120.5, 2)
    unlock_sticker(conn, "alice", "star_sticker")

    c = conn.cursor()
    c.execute("SELECT sync_pending FROM login_info WHERE username='alice'")
    assert c.fetchone()[0] == 1
    c.execute("SELECT sync_pending FROM progress_tracking WHERE username='alice' AND game_name='math_game'")
    assert c.fetchone()[0] == 1
    c.execute("SELECT sync_pending FROM rewards WHERE username='alice' AND sticker_name='star_sticker'")
    assert c.fetchone()[0] == 1

    mark_synced(conn)

    c.execute("SELECT sync_pending FROM login_info WHERE username='alice'")
    assert c.fetchone()[0] == 0
    c.execute("SELECT sync_pending FROM progress_tracking WHERE username='alice' AND game_name='math_game'")
    assert c.fetchone()[0] == 0
    c.execute("SELECT sync_pending FROM rewards WHERE username='alice' AND sticker_name='star_sticker'")
    assert c.fetchone()[0] == 0

    conn.close()
    print("Test passed!")

if __name__ == "__main__":
    test_sync_function()
