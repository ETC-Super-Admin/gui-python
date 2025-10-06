import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_sender_db():
    """
    Initializes the SQLite database. It checks for an old 'senders' table schema
    and replaces it with the new one, ensuring compatibility by dropping the old table.
    """
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        # Check if the table exists and has the old 'address' column
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='senders'")
        table_exists = cursor.fetchone()
        if table_exists:
            cursor.execute("PRAGMA table_info(senders)")
            columns = [info[1] for info in cursor.fetchall()]
            # If 'address' column exists, it's the old schema. Drop it to recreate it.
            if 'address' in columns:
                cursor.execute("DROP TABLE senders")

        # Create the table with the new schema if it doesn't exist or was just dropped
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS senders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_code TEXT NOT NULL,
                name TEXT NOT NULL,
                address_detail TEXT NOT NULL,
                sub_district TEXT NOT NULL,
                district TEXT NOT NULL,
                province TEXT NOT NULL,
                post_code TEXT NOT NULL,
                tel TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_sender(inventory_code, name, address_detail, sub_district, district, province, post_code, tel):
    """Adds a new sender to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO senders (inventory_code, name, address_detail, sub_district, district, province, post_code, tel) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel))
            conn.commit()
            return True, "Sender added successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"


def get_all_senders():
    """Retrieves all senders from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel 
            FROM senders ORDER BY created_at DESC
        """)
        senders_data = cursor.fetchall()
        return [dict(row) for row in senders_data]

def update_sender(sender_id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel):
    """Updates an existing sender's details."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE senders SET 
                              inventory_code = ?,
                              name = ?,
                              address_detail = ?,
                              sub_district = ?,
                              district = ?,
                              province = ?,
                              post_code = ?,
                              tel = ?
                          WHERE id = ?""",
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, sender_id))
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

def get_distinct_inventory_codes():
    """Retrieves a unique list of all inventory codes from the senders table."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT inventory_code FROM senders ORDER BY inventory_code")
        codes = cursor.fetchall()
        return [row[0] for row in codes]