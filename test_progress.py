import unittest
from datetime import datetime
from database import upsert_progress, get_progress, connect_db, init_db, ensure_user

class TestProgressTracking(unittest.TestCase):

    def setUp(self):
        init_db(drop_existing=True)  # resetuj bazu da se ne zakljuca iz razloga sto polsije nema pristup
        self.username = "test_user"
        self.game_name = "test_game"
        self.level = 3
        self.time_sec = 45.0
        self.mistakes = 1

        # provjera za usera da postoji da je validan
        ensure_user(self.username, "testpass")

    def test_upsert_and_get_progress(self):
        upsert_progress(self.username, self.game_name, self.level, self.time_sec, self.mistakes)

        # citanje progresa cijelog redoslijedom 
        progress = get_progress(self.username, self.game_name)

        self.assertIsNotNone(progress)
        self.assertEqual(progress['best_level'], self.level)
        self.assertAlmostEqual(progress['best_time'], self.time_sec, delta=0.1)
        self.assertEqual(progress['mistakes'], self.mistakes)

      
      # provjera datuma i vremena 
      
        self.assertIsInstance(datetime.strptime(progress['last_played'], "%Y-%m-%d %H:%M:%S"), datetime)

    def tearDown(self):
        # brisanje podataka kada se test izzvrsiS
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM progress_tracking WHERE username=?", (self.username,))
        cursor.execute("DELETE FROM login_info WHERE username=?", (self.username,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    unittest.main()
