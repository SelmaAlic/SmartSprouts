import sqlite3  # or your database library

def authenticate(username, encrypted_password):
    # Connect to the database
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    # Check if the user exists and password matches
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    conn.close()

    if result:
        stored_encrypted_password = result[0]
        if encrypted_password == stored_encrypted_password:
            return True  # Authentication successful
        else:
            return False  # Wrong password
    else:
        return False  # User does not exist
#harunharun