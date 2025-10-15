import sqlite3

DATABASE_NAME = "app_database.db"

def initialize_receiver_db():
    """
    Initializes the database and migrates the old single 'receivers' table 
    to a new structure with 'receiver_identities' and 'receiver_addresses' tables.
    """
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()

        # Check if migration is needed by looking for the old 'receivers' table schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='receivers'")
        table_exists = cursor.fetchone()
        
        is_migrated = False
        if table_exists:
            cursor.execute("PRAGMA table_info(receivers)")
            columns = [info[1] for info in cursor.fetchall()]
            # If 'receiver_identity_id' exists, we assume it's already migrated
            if 'receiver_identity_id' in columns:
                is_migrated = True

        # --- Create new tables (will be ignored if they already exist) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receiver_identities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                tel TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS receiver_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receiver_identity_id INTEGER NOT NULL,
                inventory_code TEXT NOT NULL,
                address_detail TEXT NOT NULL,
                sub_district TEXT NOT NULL,
                district TEXT NOT NULL,
                province TEXT NOT NULL,
                post_code TEXT NOT NULL,
                delivery_by TEXT NOT NULL,
                zone TEXT,
                note TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (receiver_identity_id) REFERENCES receiver_identities (id) ON DELETE CASCADE
            )
        """)

        # --- Schema Migration for 'note' column ---
        cursor.execute("PRAGMA table_info(receiver_addresses)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'note' not in columns:
            try:
                print("Migration required: Adding 'note' column to 'receiver_addresses' table...")
                cursor.execute("ALTER TABLE receiver_addresses ADD COLUMN note TEXT")
                print("Migration completed successfully.")
                conn.commit()
            except Exception as e:
                print(f"Migration for 'note' column failed: {e}")
                conn.rollback()

        if table_exists and not is_migrated:
            print("Migration required: Migrating 'receivers' table...")
            try:
                # Rename old table to start transaction-like block
                cursor.execute("ALTER TABLE receivers RENAME TO receivers_old")

                # Populate receiver_identities from old table
                cursor.execute("INSERT INTO receiver_identities (name, tel) SELECT DISTINCT name, tel FROM receivers_old")

                # Populate receiver_addresses
                cursor.execute("""
                    INSERT INTO receiver_addresses (
                        receiver_identity_id, inventory_code, address_detail, sub_district, 
                        district, province, post_code, delivery_by, zone, created_at
                    )
                    SELECT 
                        ri.id,
                        ro.inventory_code, ro.address_detail, ro.sub_district, 
                        ro.district, ro.province, ro.post_code, ro.delivery_by, ro.zone, ro.created_at
                    FROM receivers_old ro
                    JOIN receiver_identities ri ON ro.name = ri.name AND ro.tel = ri.tel
                """)
                
                cursor.execute("DROP TABLE receivers_old")
                print("Migration completed successfully.")
                conn.commit()
            except Exception as e:
                print(f"Migration failed: {e}. Rolling back.")
                conn.rollback()
                # Attempt to restore old table if rename succeeded but rest failed
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='receivers_old'")
                if cursor.fetchone():
                    cursor.execute("ALTER TABLE receivers_old RENAME TO receivers")
                raise e
        
        conn.commit()

# --- New Query Functions ---

def add_receiver_identity(name, tel):
    """Adds a new unique receiver and returns their ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO receiver_identities (name, tel) VALUES (?, ?)", (name, tel))
            conn.commit()
            return cursor.lastrowid, "Receiver added."
        except sqlite3.IntegrityError:
            # If already exists, find and return the ID
            cursor.execute("SELECT id FROM receiver_identities WHERE name = ?", (name,))
            existing_id = cursor.fetchone()
            return (existing_id[0], "Receiver already exists.") if existing_id else (None, "Failed to retrieve existing receiver.")
        except sqlite3.Error as e:
            return None, f"Database error: {e}"

def add_receiver_address(receiver_identity_id, data):
    """Adds a new address for a given receiver."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO receiver_addresses (
                    receiver_identity_id, inventory_code, address_detail, sub_district, 
                    district, province, post_code, delivery_by, zone, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                receiver_identity_id, data['inventory_code'], data['address_detail'], data['sub_district'],
                data['district'], data['province'], data['post_code'], data['delivery_by'], data.get('zone'), data.get('note')
            ))
            conn.commit()
            return True, "Address added successfully."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_all_receiver_identities():
    """Retrieves all unique receivers and includes a count of their addresses."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ri.id, 
                ri.name, 
                ri.tel, 
                COUNT(ra.id) as address_count
            FROM receiver_identities ri
            LEFT JOIN receiver_addresses ra ON ri.id = ra.receiver_identity_id
            GROUP BY ri.id
            ORDER BY ri.name
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_addresses_for_receiver(receiver_identity_id):
    """Retrieves all addresses for a specific receiver."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receiver_addresses WHERE receiver_identity_id = ? ORDER BY created_at DESC", (receiver_identity_id,))
        return [dict(row) for row in cursor.fetchall()]

def update_receiver_identity(receiver_id, name, tel):
    """Updates a receiver's name and telephone."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE receiver_identities SET name = ?, tel = ? WHERE id = ?", (name, tel, receiver_id))
            conn.commit()
            return True, "Receiver updated."
        except sqlite3.IntegrityError:
            return False, "That name is already taken."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def update_receiver_address(address_id, data):
    """Updates a specific address."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE receiver_addresses SET
                inventory_code = ?, address_detail = ?, sub_district = ?, district = ?,
                province = ?, post_code = ?, delivery_by = ?, zone = ?, note = ?
                WHERE id = ?
            """, (
                data['inventory_code'], data['address_detail'], data['sub_district'], data['district'],
                data['province'], data['post_code'], data['delivery_by'], data.get('zone'), data.get('note'), address_id
            ))
            conn.commit()
            return True, "Address updated."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_receiver_identity(receiver_id):
    """Deletes a receiver and all their associated addresses (due to CASCADE)."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM receiver_identities WHERE id = ?", (receiver_id,))
            conn.commit()
            return True, "Receiver and all addresses deleted."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def delete_receiver_address(address_id):
    """Deletes a single address."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM receiver_addresses WHERE id = ?", (address_id,))
            conn.commit()
            return True, "Address deleted."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_receiver_address_by_id(address_id):
    """Retrieves a single address by its ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receiver_addresses WHERE id = ?", (address_id,))
        data = cursor.fetchone()
        return dict(data) if data else None

def find_exact_address(receiver_identity_id, address_detail, post_code):
    """Finds an address for a specific receiver to prevent duplicates."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM receiver_addresses 
            WHERE receiver_identity_id = ? AND address_detail = ? AND post_code = ?
        """, (receiver_identity_id, address_detail, post_code))
        data = cursor.fetchone()
        return dict(data) if data else None

def get_all_receiver_addresses():
    """Retrieves all addresses from the database, joined with receiver identity info."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ri.name,
                ri.tel,
                ra.inventory_code,
                ra.address_detail,
                ra.sub_district,
                ra.district,
                ra.province,
                ra.post_code,
                ra.delivery_by,
                ra.zone,
                ra.note
            FROM receiver_addresses ra
            JOIN receiver_identities ri ON ra.receiver_identity_id = ri.id
            ORDER BY ri.name, ra.created_at
        """)
        return [dict(row) for row in cursor.fetchall()]

def set_default_address(receiver_identity_id, address_id):
    """Sets a specific address as the default for a receiver, clearing any previous default."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            # First, clear any existing default for this receiver
            cursor.execute("UPDATE receiver_addresses SET is_default = 0 WHERE receiver_identity_id = ?", (receiver_identity_id,))
            # Then, set the new default
            cursor.execute("UPDATE receiver_addresses SET is_default = 1 WHERE id = ? AND receiver_identity_id = ?", (address_id, receiver_identity_id))
            conn.commit()
            return True, "Default address set."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

def get_receiver_identity_by_id(receiver_id):
    """Retrieves a single receiver identity by their ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM receiver_identities WHERE id = ?", (receiver_id,))
        data = cursor.fetchone()
        return dict(data) if data else None
