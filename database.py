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
                x integer,
                y integer,
                map_number varchar(50)
            )
        """
        )
        self.conn.commit()
        res = self.cursor.execute("""select id from progress""")
        am = 0
        for _ in res:
            am += 1
        if am == 0:
            self.cursor.execute("""insert into progress (id, x, y, map_number) values (1, 960, 544, 'spawn')""")
            self.conn.commit()

    def save_progress(self, x, y, number):
        self.cursor.execute(
            "INSERT OR REPLACE INTO progress (id, x, y, map_number) VALUES (1, ?, ?, ?)", (x, y, number)
        )
        self.conn.commit()

    def load_progress(self):
        res = self.cursor.execute("SELECT x, y, map_number FROM progress WHERE id = 1")
        x, y, map_name = 0, 0, ''
        for one, two, mapus in res:
            x, y, map_name = one, two, mapus
        # print(x, y, map_name)
        return [x, y, map_name]

    def close(self):
        self.conn.close()
