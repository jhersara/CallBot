import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect("trades.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            type TEXT,
            lot REAL,
            profit REAL,
            date TEXT
        )
        ''')

        self.conn.commit()