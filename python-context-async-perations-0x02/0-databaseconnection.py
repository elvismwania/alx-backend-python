#!/usr/bin/env python3
import sqlite3

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Usage example:
if __name__ == "__main__":
    db_file = "example.db"

    # (Optional) Create sample table and data if not exists
    with sqlite3.connect(db_file) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob')")
        conn.commit()

    # Use the custom context manager
    with DatabaseConnection(db_file) as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        for row in results:
            print(row)
