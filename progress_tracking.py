import sqlite3
from datetime import datetime

DB_PATH = "database.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_progress_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            game_name TEXT NOT NULL,
            best_level INTEGER DEFAULT 0,
            best_time REAL DEFAULT NULL,
            mistakes INTEGER DEFAULT 0,
            last_played DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(username, game_name),
            FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def get_progress(username, game_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT best_level, best_time, mistakes, last_played
        FROM progress_tracking
        WHERE username=? AND game_name=?
    ''', (username, game_name))
    result = cursor.fetchone()
    conn.close()
    return result  # returns tuple or None

def update_progress(username, game_name, level, time_sec, mistakes):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT best_level, best_time FROM progress_tracking WHERE username=? AND game_name=?', (username, game_name))
    row = cursor.fetchone()

    if row:
        best_level, best_time = row
     
        if (level > best_level) or (level == best_level and (best_time is None or time_sec < best_time)):
            cursor.execute('''
                UPDATE progress_tracking
                SET best_level=?, best_time=?, mistakes=?, last_played=?
                WHERE username=? AND game_name=?
            ''', (level, time_sec, mistakes, datetime.now(), username, game_name))
    else:
       
        cursor.execute('''
            INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, game_name, level, time_sec, mistakes))

    conn.commit()
    conn.close()

create_progress_table()
