import sqlitecloud
import requests

def connect_cloud(cloud_conn_str):
    return sqlitecloud.connect(cloud_conn_str)

def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False