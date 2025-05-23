from net_util import is_internet_available

def cloud_sync(username, local_conn, cloud_conn, tables, sync_manager_ready):

    if not is_internet_available():
        print("No internet connection. Please connect and try again.")
        return False

    if not sync_manager_ready:
        print("Sync manager is not ready. Please log in to sync your data.")
        return False

    try:
        sync_all(local_conn, cloud_conn, tables, username)
        print("Sync successful!")
        return True
    except Exception as e:
        print(f"Sync failed. Try again later. Error: {e}")
        return False

def sync_all(local_conn, cloud_conn, tables, username):
    for table in tables:
        sync_table(local_conn, cloud_conn, table, username)

def sync_table(local_conn, cloud_conn, table, username):
    
    local_rows, columns = get_rows_to_sync(local_conn, table, username)
    for row in local_rows:
        upsert_row(cloud_conn, table, columns, row)
        cursor = local_conn.cursor()
        cursor.execute(f"UPDATE {table} SET sync_pending=0 WHERE id=?", (row[columns.index('id')],))
    cloud_conn.commit()
    local_conn.commit()

   
    cloud_rows, cloud_columns = get_cloud_rows(cloud_conn, table, username)
    for c_row in cloud_rows:
        local_row = get_row_by_id(local_conn, table, c_row[cloud_columns.index('id')])
        if local_row is None:
            upsert_row(local_conn, table, cloud_columns, c_row)
        else:
            local_idx = {col: i for i, col in enumerate(columns)}
            cloud_idx = {col: i for i, col in enumerate(cloud_columns)}
            local_lm = local_row[local_idx['last_modified']]
            cloud_lm = c_row[cloud_idx['last_modified']]
            if cloud_lm > local_lm:
                upsert_row(local_conn, table, cloud_columns, c_row)
    local_conn.commit()

def get_rows_to_sync(conn, table, username):
    cursor = conn.cursor()
    rows = cursor.execute(
        f"SELECT * FROM {table} WHERE sync_pending=1 AND username=?", (username,)
    ).fetchall()
    columns = [d[0] for d in cursor.description]
    return rows, columns

def get_cloud_rows(cloud_conn, table, username):
    cursor = cloud_conn.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE username=?", (username,))
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return rows, columns

def get_row_by_id(conn, table, row_id):
    cursor = conn.cursor()
    return cursor.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,)).fetchone()

def upsert_row(conn, table, columns, values):
    cursor = conn.cursor()
    set_clause = ', '.join([f"{col}=?" for col in columns if col != 'id'])
    update_sql = f"UPDATE {table} SET {set_clause} WHERE id=?"
    update_values = [v for c, v in zip(columns, values) if c != 'id'] + [values[columns.index('id')]]
    cursor.execute(update_sql, update_values)
    if cursor.rowcount == 0:
        placeholders = ','.join(['?'] * len(columns))
        insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)

