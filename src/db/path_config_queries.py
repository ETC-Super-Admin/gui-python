import sqlite3

_DATABASE_PATH = "app_database.db"

def set_database_path(db_path):
    """Sets the global database path. Should be called before any database operations."""
    global _DATABASE_PATH
    _DATABASE_PATH = db_path

def initialize_path_config_db(db_path=None):
    """Initializes the database and creates the inventory_path_configs table if it doesn't exist."""
    if db_path:
        set_database_path(db_path)
    with sqlite3.connect(_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_path_configs (
                inventory_code TEXT PRIMARY KEY,
                template_dir TEXT NOT NULL
            )
        """)
        conn.commit()

def add_path_config(inventory_code, template_dir):
    """Adds a new path configuration."""
    with sqlite3.connect(_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO inventory_path_configs (inventory_code, template_dir) VALUES (?, ?)", (inventory_code, template_dir))
            conn.commit()
            return True, "Path configuration added."
        except sqlite3.IntegrityError:
            return False, f"Inventory code ''{inventory_code}'' already exists."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def update_path_config(inventory_code, template_dir):
    """Updates an existing path configuration."""
    with sqlite3.connect(_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE inventory_path_configs SET template_dir = ? WHERE inventory_code = ?", (template_dir, inventory_code))
            conn.commit()
            return True, "Path configuration updated."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_path_config(inventory_code):
    """Deletes a path configuration."""
    with sqlite3.connect(_DATABASE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM inventory_path_configs WHERE inventory_code = ?", (inventory_code,))
            conn.commit()
            return True, "Path configuration deleted."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_all_path_configs():
    """Retrieves all path configurations from the database."""
    with sqlite3.connect(_DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT inventory_code, template_dir FROM inventory_path_configs ORDER BY inventory_code")
        configs = cursor.fetchall()
        return [dict(row) for row in configs]