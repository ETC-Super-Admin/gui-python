import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_sender_db():
    """Initializes the SQLite database and creates the senders table if it doesn't exist."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS senders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_code TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                post_code TEXT NOT NULL,
                tel TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_sender(inventory_code, name, address, post_code, tel):
    """Adds a new sender to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO senders (inventory_code, name, address, post_code, tel) VALUES (?, ?, ?, ?, ?)",
                           (inventory_code, name, address, post_code, tel))
            conn.commit()
            return True, "Sender added successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_all_senders():
    """Retrieves all senders from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("SELECT id, inventory_code, name, address, post_code, tel FROM senders ORDER BY created_at DESC")
        senders_data = cursor.fetchall()
        return [dict(row) for row in senders_data]

def update_sender(sender_id, inventory_code, name, address, post_code, tel):
    """Updates an existing sender's details."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE senders SET 
                              inventory_code = ?,
                              name = ?,
                              address = ?,
                              post_code = ?,
                              tel = ?
                          WHERE id = ?""",
                           (inventory_code, name, address, post_code, tel, sender_id))
            conn.commit()
            return True, "Sender updated successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_sender(sender_id):
    """Deletes a sender from the database by ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM senders WHERE id = ?", (sender_id,))
            conn.commit()
            return True, "Sender deleted successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"