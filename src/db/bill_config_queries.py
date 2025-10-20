import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_bill_config_db():
    """Initializes the database and creates the bill_configs table if it doesn't exist."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT NOT NULL,
                config_type INTEGER NOT NULL,
                focus TEXT NOT NULL,
                check_text TEXT,
                value TEXT
            )
        """)
        # Remove the old 'By Collect Column' type if it exists
        cursor.execute("DELETE FROM bill_configs WHERE config_type = 2")
        conn.commit()

def add_bill_config(data):
    """Adds a new bill configuration."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO bill_configs 
                           (field_name, config_type, focus, check_text, value) 
                           VALUES (?, ?, ?, ?, ?)""", 
                           (data['field_name'], data['config_type'], data['focus'], data['check'], data['value']))
            conn.commit()
            return True, "Configuration added."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_all_bill_configs():
    """Retrieves all bill configurations from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, field_name, config_type, focus, check_text, value FROM bill_configs ORDER BY field_name")
        configs = cursor.fetchall()
        return [dict(row) for row in configs]

def update_bill_config(config_id, data):
    """Updates an existing bill configuration."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE bill_configs SET 
                           field_name = ?, config_type = ?, focus = ?, check_text = ?, value = ?
                           WHERE id = ?""",
                           (data['field_name'], data['config_type'], data['focus'], data['check'], data['value'], config_id))
            conn.commit()
            return True, "Configuration updated."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_bill_config(config_id):
    """Deletes a bill configuration."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM bill_configs WHERE id = ?", (config_id,))
            conn.commit()
            return True, "Configuration deleted."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
