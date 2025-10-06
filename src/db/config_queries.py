import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_config_db():
    """Initializes the database and creates the app_config table if it doesn't exist."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

def save_config(key, value):
    """Saves a key-value pair to the config table. Replaces the value if the key already exists."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT OR REPLACE INTO app_config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            return True, "Configuration saved."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_config(key, default=None):
    """Retrieves a value from the config table for a given key."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else default
