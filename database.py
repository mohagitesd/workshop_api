import sqlite3

DB_NAME = "museofile.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # create users table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL
    )
    """
    )

    # create favorites table with per-user favorites
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        musee_id TEXT NOT NULL,
        name TEXT NOT NULL,
        city TEXT,
        department TEXT,
        user_id INTEGER NOT NULL,
        UNIQUE(musee_id, user_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    )

    conn.commit()
    conn.close()


# initialize DB on module import
init_db()
