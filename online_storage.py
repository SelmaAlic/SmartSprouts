# pip install sqlitecloud

import sqlitecloud
from datetime import datetime, timezone
import keyring
from offline_data_storage import GameProgressDB 


SQLITE_CLOUD_URL = "sqlitecloud://your-cluster.sqlite.cloud:8860"
DATABASE_NAME = "game_progress"
API_KEY_ID = "game_app_key"

# sync logic with cloud
class SQLiteCloudSync:
    def __init__(self):
        self.api_key = keyring.get_password("GameEduApp", API_KEY_ID)
        self.conn = None

    def _connect(self) -> bool:
        try:
            self.conn = sqlitecloud.connect(
                f"{SQLITE_CLOUD_URL}/{DATABASE_NAME}?apikey={self.api_key}"
            )
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def push_changes(self, local_db: GameProgressDB, last_sync: datetime) -> bool:
        """Use your existing class's methods"""
        if not self._connect():
            return False

        try:
            # get unsynced data 
            unsynced_progress = local_db.get_unsynced_progress(last_sync)
            unsynced_achievements = local_db.get_unsynced_rewards(last_sync)

            # push data to cloud
            if unsynced_progress:
                self.conn.executemany(
                    "INSERT OR REPLACE INTO user_games VALUES (?,?,?,?,?)",
                    unsynced_progress
                )

            if unsynced_achievements:
                self.conn.executemany(
                    "INSERT OR IGNORE INTO user_achievements VALUES (?,?,?)",
                    unsynced_achievements
                )

            self.conn.commit()
            return True
        except sqlitecloud.DatabaseError as e:
            print(f"Push error: {str(e)}")
            return False
        finally:
            if self.conn:
                self.conn.close()

    def pull_changes(self, local_db: GameProgressDB, last_sync: datetime) -> bool:
        if not self._connect():
            return False

        try:
            # pull progress
            cloud_progress = self.conn.execute(
                "SELECT * FROM user_games WHERE last_updated > ?",
                (last_sync.isoformat(),)
            ).fetchall()

            # pull rewards
            cloud_rewards = self.conn.execute(
                "SELECT * FROM user_achievements WHERE unlocked_at > ?",
                (last_sync.isoformat(),)
            ).fetchall()


            local_db.import_progress(cloud_progress)
            local_db.import_rewards(cloud_rewards)
            
            return True
        except sqlitecloud.DatabaseError as e:
            print(f"Pull error: {str(e)}")
            return False
        finally:
            if self.conn:
                self.conn.close()

# sync management

class SyncManager:
    def __init__(self, local_db: GameProgressDB):
        self.local_db = local_db
        self.cloud_sync = SQLiteCloudSync()
        self.last_sync = datetime.now(timezone.utc)

    def full_sync(self) -> bool:
        try:
            if not self.cloud_sync.push_changes(self.local_db, self.last_sync):
                return False

            if not self.cloud_sync.pull_changes(self.local_db, self.last_sync):
                return False

            self.last_sync = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Sync failed: {str(e)}")
            return False

# test
if __name__ == "__main__":

    my_local_db = GameProgressDB() 
    sync_manager = SyncManager(my_local_db)
    
    if sync_manager.full_sync():
        print("Sync successful!")
    else:
        print("Sync failed")

