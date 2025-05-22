from database import connect_db, create_tables
from cloud_api import connect_cloud
from sync import run_sync
import sqlitecloud

if __name__ == "__main__":
    cloud_conn_str = "sqlitecloud://cz0s4hgxnz.g6.sqlite.cloud:8860/database.db?apikey=w1Q0wgb3dEbBL9iiUtDIO8uh29bg3Trn8b9pLmt9Qvg"
    tables = ["login_info", "progress_tracking", "rewards"]
    current_user= "johndoe"

    local_conn = connect_db()
    create_tables(local_conn)
    cloud_conn = connect_cloud(cloud_conn_str)

    sync_manager_ready = True  

    run_sync(local_conn, cloud_conn, tables, current_user, sync_manager_ready)

    local_conn.close()
    cloud_conn.close()


