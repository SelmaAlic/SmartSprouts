import sqlite3
import bcrypt

def authenticate(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM login_info WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return False