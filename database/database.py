import sqlite3
from config.settings import DB_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age TEXT,
                gender TEXT,
                phone TEXT,
                address TEXT,
                emer_name TEXT,
                emer_rel TEXT,
                emer_phone TEXT,
                history TEXT,
                symptoms TEXT,
                diagnosis TEXT,
                visit_date TEXT
            )
        """)
        self.conn.commit()

    def save_patient(self, record):
        query = """
            INSERT INTO patients (
                name, age, gender, phone, address,
                emer_name, emer_rel, emer_phone,
                history, symptoms, diagnosis, visit_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, record)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.conn.close()