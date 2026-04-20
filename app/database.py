import sqlite3

class Database:
    DB_FILE = "hospital_records.db"

    COLUMNS = [
        ("id",         "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("name",       "TEXT NOT NULL"),
        ("age",        "TEXT"),
        ("gender",     "TEXT"),
        ("email",      "TEXT"), 
        ("phone",      "TEXT"),
        ("address",    "TEXT"),
        ("emer_name",  "TEXT"),
        ("emer_rel",   "TEXT"),
        ("emer_phone", "TEXT"),
        ("history",    "TEXT"),
        ("symptoms",   "TEXT"),
        ("diagnosis",  "TEXT"),
        ("visit_date", "TEXT"),
    ]

    DATA_COLUMNS = [col for col, _ in COLUMNS if col != "id"]

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        col_defs = ",\n                ".join(
            f"{col} {dtype}" for col, dtype in self.COLUMNS
        )
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS patients ({col_defs})")
        self.conn.commit()

    def save(self, data: tuple) -> int:
        placeholders = ", ".join("?" * len(self.DATA_COLUMNS))
        cols = ", ".join(self.DATA_COLUMNS)
        self.cursor.execute(f"INSERT INTO patients ({cols}) VALUES ({placeholders})", data)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.conn.close()