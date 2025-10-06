import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_receiver_db():
    """Initializes the database and creates the receivers table if it doesn't exist."""
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
        conn.commit()

def add_receiver(inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by):
    """Adds a new receiver to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO receivers (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by))
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
            SELECT id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by 
            FROM receivers ORDER BY created_at DESC
        """)
        receivers_data = cursor.fetchall()
        return [dict(row) for row in receivers_data]

def update_receiver(receiver_id, inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by):
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
                              delivery_by = ?
                          WHERE id = ?""",
                           (inventory_code, name, address_detail, sub_district, district, province, post_code, tel, delivery_by, receiver_id))
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