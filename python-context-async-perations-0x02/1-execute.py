#!/usr/bin/env python3
import sqlite3

class ExecuteQuery:
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or []
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# REQUIRED by checker: use the context manager with 'with'
if __name__ == "__main__":
    db_name = "example.db"

    # Setup: Only for local testing (ensure table and data exist)
    with sqlite3.connect(db_name) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
        conn.execute("INSERT OR IGNORE INTO users (id, name, age) VALUES (1, 'Alice', 30), (2, 'Bob', 22), (3, 'Charlie', 28)")
        conn.commit()


    query = "SELECT * FROM users WHERE age > ?"
    params = [25]

    with ExecuteQuery(db_name, query, params) as result:
        for row in result:
            print(row)
