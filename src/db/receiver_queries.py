import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_receiver_db():
    """
    Initializes the database, creates the receivers table if it doesn't exist,
    and adds the 'zone' column if it's missing.
    """
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_code TEXT NOT NULL,
                name TEXT NOT NULL,
                address_detail TEXT NOT NULL,
                sub_district TEXT NOT NULL,
                district TEXT NOT NULL,
                province TEXT NOT NULL,
                post_code TEXT NOT NULL,
                tel TEXT NOT NULL,
                delivery_by TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add the 'zone' column if it doesn't exist for backward compatibility
        try:
            cursor.execute("ALTER TABLE receivers ADD COLUMN zone TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise  # Re-raise error if it's not about a duplicate column

        conn.commit()

def add_receiver(inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone=None):
    """Adds a new receiver to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO receivers (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone))
            conn.commit()
            return True, "Receiver added successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_all_receivers():
    """Retrieves all receivers from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone 
            FROM receivers ORDER BY created_at DESC
        """)
        receivers_data = cursor.fetchall()
        return [dict(row) for row in receivers_data]

def update_receiver(receiver_id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone=None):
    """Updates an existing receiver's details."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE receivers SET 
                              inventory_code = ?,
                              name = ?,
                              address_detail = ?,
                              sub_district = ?,
                              district = ?,
                              province = ?,
                              post_code = ?,
                              tel = ?,
                              delivery_by = ?,
                              zone = ?
                          WHERE id = ?""",
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, zone, receiver_id))
            conn.commit()
            return True, "Receiver updated successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_receiver(receiver_id):
    """Deletes a receiver from the database by ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM receivers WHERE id = ?", (receiver_id,))
            conn.commit()
            return True, "Receiver deleted successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_receiver_by_id(receiver_id):
    """Retrieves a single receiver from the database by its ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receivers WHERE id = ?", (receiver_id,))
        receiver_data = cursor.fetchone()
        return dict(receiver_data) if receiver_data else None