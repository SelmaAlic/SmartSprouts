import sqlite3

conn = sqlite3.connect('cognitive_games.db')
cursor = conn.cursor()

cursor.execute('''
DROP TABLE IF EXISTS login_info
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS login_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password BLOB NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS progress_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    game_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    time_played DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    sticker_name TEXT NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE
)
''')

conn.commit()
conn.close()

print("Database updated and ready with secure password storage.")
