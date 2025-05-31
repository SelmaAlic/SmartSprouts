import sqlitecloud

def connect_cloud(cloud_conn_str):
    return sqlitecloud.connect(cloud_conn_str)
