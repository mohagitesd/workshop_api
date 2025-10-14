import sqlite3

DB_NAME = "museofile.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        hashed_password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        museum_id TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()
