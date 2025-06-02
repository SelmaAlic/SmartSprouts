import sqlite3
from encryption import verify_encryption

def authenticate(username, raw_password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM login_info WHERE username = ?", (username,)) 
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_encrypted_password = result[0]
        return verify_encryption(raw_password, stored_encrypted_password)
    return False