import sqlite3


class DatabaseManager:
    def __init__(self, db_name="game_progress.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                location TEXT
            )
        """
        )
        self.conn.commit()

    def save_progress(self, location):
        self.cursor.execute(
            "INSERT OR REPLACE INTO progress (id, location) VALUES (1, ?)", (location,)
        )
        self.conn.commit()

    def load_progress(self):
        self.cursor.execute("SELECT location FROM progress WHERE id = 1")
        result = self.cursor.fetchone()
        return result[0] if result else "start"

    def close(self):
        self.conn.close()
