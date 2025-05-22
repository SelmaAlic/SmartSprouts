import sqlitecloud
import datetime

cloud_conn_str = "sqlitecloud://cz0s4hgxnz.g6.sqlite.cloud:8860/database.db?apikey=w1Q0wgb3dEbBL9iiUtDIO8uh29bg3Trn8b9pLmt9Qvg"
conn = sqlitecloud.connect(cloud_conn_str)
cursor = conn.cursor()

now = datetime.datetime.now(datetime.timezone.utc).isoformat()

users = [
    ("alice", b"alicepassword", 1, now),
    ("bob", b"bobpassword", 1, now)
]
for username, password, sync_pending, last_modified in users:
    cursor.execute(
        "INSERT INTO login_info (username, password, sync_pending, last_modified) VALUES (?, ?, ?, ?)",
        (username, password, sync_pending, last_modified)
    )
conn.commit()
print(" Users added.")


cursor.execute("SELECT id, username, last_modified FROM login_info")
rows = cursor.fetchall()
print("Current users in cloud database:")
for row in rows:
    print(row)

cursor.execute(
    "INSERT INTO progress_tracking (username, game_name, best_level, best_time, mistakes, sync_pending, last_modified) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("alice", "MathGame", 3, 120.5, 2, 1, now)
)
conn.commit()
print(" Progress for Alice added.")

cursor.execute("SELECT * FROM progress_tracking")
print("Progress tracking entries:")
for row in cursor.fetchall():
    print(row)

conn.close()
