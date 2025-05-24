import sqlite3

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        if col[1] == column_name:
            return True
    return False

def connect_db():
    conn = sqlite3.connect('database.db') 
    conn.execute("PRAGMA foreign_keys = ON")  
    return conn

def create_tables(conn):
    cursor = conn.cursor()

    # Create login_info table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        sync_pending INTEGER DEFAULT 1,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP           
    )
    ''')

    # Create progress_tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        game_name TEXT NOT NULL,
        best_level INTEGER DEFAULT 0,
        best_time REAL,
        mistakes INTEGER DEFAULT 0,
        last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        sync_pending INTEGER DEFAULT 1,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           
        UNIQUE(username, game_name)
                  
    )
    ''')

    # Add 'best_level' column if missing
    if not column_exists(cursor, 'progress_tracking', 'best_level'):
        cursor.execute("ALTER TABLE progress_tracking ADD COLUMN best_level INTEGER DEFAULT 0")
        print("✅ Added missing column 'best_level' to progress_tracking table")

    # Add 'mistakes' column if missing
    if not column_exists(cursor, 'progress_tracking', 'mistakes'):
        cursor.execute("ALTER TABLE progress_tracking ADD COLUMN mistakes INTEGER DEFAULT 0")
        print("✅ Added missing column 'mistakes' to progress_tracking table")

    # Create rewards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        sticker_name TEXT NOT NULL,
        unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        sync_pending INTEGER DEFAULT 1,
        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,           
        FOREIGN KEY(username) REFERENCES login_info(username) ON DELETE CASCADE          
    )
    ''')

    conn.commit()

def show_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("✅ Tables in the database:")
    for table in tables:
        print("•", table[0])

def get_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM login_info")
    return cursor.fetchall()

def get_progress(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_tracking")
    return cursor.fetchall()

def get_rewards(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rewards")
    return cursor.fetchall()

def add_user(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO login_info (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error adding user '{username}': {e}")

def close_db(conn):
    conn.close()

def print_database_contents(conn):
    show_tables(conn)

    print("\n👤 Users in login_info:")
    try:
        users = get_users(conn)
        if users:
            for user in users:
                print("ID:", user[0], "| Username:", user[1])
        else:
            print("No users found.")
    except sqlite3.Error as e:
        print("Error reading login_info:", e)

    print("\n🎮 Progress tracking entries:")
    try:
        progress = get_progress(conn)
        if progress:
            for entry in progress:
                print(entry)
        else:
            print("No progress records found.")
    except sqlite3.Error as e:
        print("Error reading progress_tracking:", e)

    print("\n🏅 Rewards entries:")
    try:
        rewards = get_rewards(conn)
        if rewards:
            for reward in rewards:
                print(reward)
        else:
            print("No rewards found.")
    except sqlite3.Error as e:
        print("Error reading rewards:", e)

if __name__ == "__main__":
    conn = connect_db()
    create_tables(conn)
    print_database_contents(conn)
    close_db(conn)
    print("\n✅ Database is ready and data displayed successfully.")