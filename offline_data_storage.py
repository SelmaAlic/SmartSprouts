import sqlite3
from datetime import datetime, timezone 
from pathlib import Path
from typing import Optional


class GameProgressDB:
    def __init__(
        self,
        db_path: Optional[str] = None,
        schema_path: Optional[str] = None,
        data_dir: Optional[str] = None
    ):
        
        # resolving base directory
        base_dir = Path(data_dir) if data_dir else Path(__file__).parent
        
        # setting paths
        self.db_path = self._resolve_path(db_path, base_dir, "game.db")
        self.schema_path = self._resolve_path(schema_path, base_dir, "schema.sql")
        
        # initializing database
        self.conn = sqlite3.connect(str(self.db_path))
        self._initialize_schema()

    def _resolve_path(
        self,
        user_path: Optional[str],
        base_dir: Path,
        default_filename: str
    ) -> Path:
        
        """Resolve paths with directory creation"""
        path = Path(user_path) if user_path else base_dir / default_filename
        path.parent.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    def _initialize_schema(self):

        """Load schema with error handling"""
        try:
            schema = self.schema_path.read_text(encoding='utf-8')
            self.conn.executescript(schema)
            self.conn.commit()
        except FileNotFoundError:
            raise RuntimeError(f"Schema file missing at {self.schema_path}")
        except sqlite3.Error as e:
            raise RuntimeError(f"Schema init failed: {str(e)}")
        
    # methods for game progress storage
    def save_progress(self, user_id: str, game_id: str, level: int, score: int):

        self.conn.execute('''
            INSERT OR REPLACE INTO prgress_tracking
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, game_id, level, score))
        self.conn.commit()

    def load_progress(self, user_id: str, game_id: str) -> dict:

        cursor = self.conn.execute('''
            SELECT * FROM progress_tracking 
            WHERE user_id = ? AND game_id = ?
        ''', (user_id, game_id))
        return dict(cursor.fetchone())

    # methods for syncing
    def get_unsynced_progress(self, last_sync: datetime) -> list:
        """Sync Method 1"""
        cursor = self.conn.execute('''
            SELECT * FROM progress_tracking
            WHERE last_updated > ?
        ''', (last_sync.isoformat(),))
        return cursor.fetchall()

    def get_unsynced_rewards(self, last_sync: datetime) -> list:
        """Sync Method 2"""
        cursor = self.conn.execute('''
            SELECT * FROM rewards
            WHERE unlocked_at > ?
        ''', (last_sync.isoformat(),))
        return cursor.fetchall()

    def import_progress(self, records: list):
        """Sync Method 3"""
        self.conn.executemany('''
            INSERT OR REPLACE INTO progress_tracking
            VALUES (?,?,?,?,?)
        ''', records)
        self.conn.commit()

    def import_rewards(self, records: list):
        """Sync Method 4"""
        self.conn.executemany('''
            INSERT OR IGNORE INTO rewards
            VALUES (?,?,?)
        ''', records)
        self.conn.commit()
