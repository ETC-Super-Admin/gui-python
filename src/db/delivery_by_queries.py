import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_delivery_db():
    """Initializes the DB, creates the table, and seeds it with initial data if empty."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS delivery_options (
                name TEXT PRIMARY KEY
            )
        """)
        # Seed with initial data if table is new
        cursor.execute("SELECT COUNT(*) FROM delivery_options")
        if cursor.fetchone()[0] == 0:
            initial_options = [("Kerry",), ("Flash",), ("J&T",), ("DHL",), ("Thai Post",)]
            cursor.executemany("INSERT INTO delivery_options (name) VALUES (?)", initial_options)
        conn.commit()

def get_all_delivery_options():
    """Retrieves all delivery options from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM delivery_options ORDER BY name")
        return [row[0] for row in cursor.fetchall()]

def add_delivery_option(name):
    """Adds a new delivery option."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO delivery_options (name) VALUES (?)", (name,))
            conn.commit()
            return True, f"Added '{name}'."
        except sqlite3.IntegrityError:
            return False, f"'{name}' already exists."

def delete_delivery_option(name):
    """Deletes a delivery option."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            # In a real-world app, you might want to check if this option is in use.
            cursor.execute("DELETE FROM delivery_options WHERE name = ?", (name,))
            conn.commit()
            return True, f"Deleted '{name}'."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def update_delivery_option(old_name, new_name):
    """Updates a delivery option and cascades the change to the receivers table."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            # Check if new name already exists
            cursor.execute("SELECT COUNT(*) FROM delivery_options WHERE name = ?", (new_name,))
            if cursor.fetchone()[0] > 0 and old_name.lower() != new_name.lower():
                return False, f"'{new_name}' already exists."
            
            cursor.execute("UPDATE delivery_options SET name = ? WHERE name = ?", (new_name, old_name))
            # Also update all receivers using the old name
            cursor.execute("UPDATE receivers SET delivery_by = ? WHERE delivery_by = ?", (new_name, old_name))
            conn.commit()
            return True, f"Updated '{old_name}' to '{new_name}'."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
