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
            id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            department TEXT
        )
    """)

    # Table to map favorites to users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        favorite_id TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(favorite_id) REFERENCES favorites(id)
    )
    """)

    # Tokens table for simple token-based auth
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()
