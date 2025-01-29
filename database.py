import sqlite3


class DatabaseManager:
    def __init__(self, db_name="game_progress.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._init_tables()
        self._init_maps()

    def _init_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS maps (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50)
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                x INTEGER,
                y INTEGER,
                map INTEGER,
                FOREIGN KEY (map) REFERENCES maps(id)
            )
        """
        )
        self.conn.commit()
        res = self.cursor.execute("""
                                  SELECT id FROM progress
                                  """)
        
        if res.fetchone() is None:
            self.cursor.execute("""
                                INSERT INTO progress (id, x, y, map) VALUES (1, 960, 544, (SELECT id FROM maps WHERE name = 'spawn'))
                                """)
            self.conn.commit()
            
    def _init_maps(self):
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO maps (id, name) VALUES (1, 'spawn')
            """
        )
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO maps (id, name) VALUES (2, 'right map')
            """
        )
        self.conn.commit()
        

    def save_progress(self, x, y, number):
        self.cursor.execute("""
                            INSERT OR REPLACE INTO progress (id, x, y, map) VALUES (1, ?, ?, (SELECT id FROM maps WHERE name = ?))
                            """, (x, y, number)
        )
        self.conn.commit()

    def load_progress(self):
        res = self.cursor.execute("""
                                  SELECT progress.x, progress.y, maps.name FROM progress JOIN maps ON progress.map = maps.id WHERE progress.id = 1
                                  """)
        row = res.fetchone()
        if row is None:
            return 0, 0, ''
        return row[0], row[1], row[2]

    def close(self):
        self.conn.close()
