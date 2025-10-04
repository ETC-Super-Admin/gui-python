import sqlite3
import hashlib

DATABASE_NAME = "app_database.db"

def initialize_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                avatar TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def hash_password(password):
    """Hashes a password using SHA256.
    WARNING: SHA256 is not recommended for password hashing in production.
    Consider using a dedicated password hashing library like `bcrypt` or `argon2`
    which are designed to be slow and resistant to brute-force attacks.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, email=None, role='user', avatar=None):
    """Adds a new user to the database."""
    password_hash = hash_password(password)
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, email, role, avatar) VALUES (?, ?, ?, ?, ?)",
                           (username, password_hash, email, role, avatar))
            conn.commit()
            return True, "User registered successfully."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                return False, "Username already exists."
            elif "UNIQUE constraint failed: users.email" in str(e):
                return False, "Email already exists."
            else:
                return False, f"Database error: {e}"

def get_user_details(username):
    """Retrieves all details of a user by username."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, avatar, created_at FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
                "role": user_data[3],
                "avatar": user_data[4],
                "created_at": user_data[5]
            }
        return None

def verify_user(username, password):
    """Verifies a user's credentials."""
    password_hash = hash_password(password)
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                       (username, password_hash))
        user = cursor.fetchone()
        return user is not None

def get_user_role(username):
    """Retrieves the role of a user."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

if __name__ == "__main__":
    initialize_db()
    print("Database initialized and 'users' table created.")

    # Example usage:
    # Add an admin user from .env
    admin_username = "admin" # Replace with actual admin username from .env
    admin_password = "123456" # Replace with actual admin password from .env
    if add_user(admin_username, admin_password, 'admin'):
        print(f"Admin user '{admin_username}' added.")
    else:
        print(f"Admin user '{admin_username}' already exists.")

    # Add a regular user
    if add_user("testuser", "password123"):
        print("User 'testuser' added.")

    # Verify users
    if verify_user("admin", "123456"):
        print("Admin user verified successfully.")
    else:
        print("Admin user verification failed.")

    if verify_user("testuser", "password123"):
        print("Test user verified successfully.")
    else:
        print("Test user verification failed.")

    if verify_user("testuser", "wrongpassword"):
        print("Test user with wrong password verified (ERROR).")
    else:
        print("Test user with wrong password verification failed (CORRECT).")

def get_all_users():
    """Retrieves all users from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, role, avatar, created_at FROM users")
        users_data = cursor.fetchall()
        users = []
        for user_data in users_data:
            users.append({
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
                "role": user_data[3],
                "avatar": user_data[4],
                "created_at": user_data[5]
            })
        return users

def update_user(user_id, username=None, password=None, email=None, role=None, avatar=None):
    """Updates an existing user's details in the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        updates = []
        params = []

        if username:
            updates.append("username = ?")
            params.append(username)
        if password:
            password_hash = hash_password(password)
            updates.append("password_hash = ?")
            params.append(password_hash)
        if email:
            updates.append("email = ?")
            params.append(email)
        if role:
            updates.append("role = ?")
            params.append(role)
        if avatar:
            updates.append("avatar = ?")
            params.append(avatar)

        if not updates:
            return False, "No fields to update."

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, tuple(params))
            conn.commit()
            return True, "User updated successfully."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                return False, "Username already exists."
            elif "UNIQUE constraint failed: users.email" in str(e):
                return False, "Email already exists."
            else:
                return False, f"Database error: {e}"

def delete_user(user_id):
    """Deletes a user from the database by ID."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0, "User deleted successfully."

if __name__ == "__main__":
    initialize_db()
    print("Database initialized and 'users' table created.")

    # Example usage:
    # Add an admin user from .env
    admin_username = "admin" # Replace with actual admin username from .env
    admin_password = "123456" # Replace with actual admin password from .env
    if add_user(admin_username, admin_password, email="admin@example.com", role='admin')[0]:
        print(f"Admin user '{admin_username}' added.")
    else:
        print(f"Admin user '{admin_username}' already exists.")

    # Add a regular user
    if add_user("testuser", "password123", email="test@example.com")[0]:
        print("User 'testuser' added.")

    # Verify users
    if verify_user("admin", "123456"):
        print("Admin user verified successfully.")
    else:
        print("Admin user verification failed.")

    if verify_user("testuser", "password123"):
        print("Test user verified successfully.")
    else:
        print("Test user verification failed.")

    if verify_user("testuser", "wrongpassword"):
        print("Test user with wrong password verified (ERROR).")
    else:
        print("Test user with wrong password verification failed (CORRECT).")

    print(f"Role of 'admin': {get_user_role('admin')}")
    print(f"Role of 'testuser': {get_user_role('testuser')}")

    # Example of new functions
    print("\n--- Testing new functions ---")
    all_users = get_all_users()
    print("All users:", all_users)

    if all_users:
        # Update a user
        user_to_update_id = all_users[0]['id']
        print(f"Updating user with ID {user_to_update_id}...")
        success, msg = update_user(user_to_update_id, email="updated_admin@example.com")
        print(f"Update result: {success}, {msg}")
        print("User after update:", get_user_details(all_users[0]['username']))

        # Delete a user
        user_to_delete_id = all_users[0]['id']
        print(f"Deleting user with ID {user_to_delete_id}...")
        success, msg = delete_user(user_to_delete_id)
        print(f"Delete result: {success}, {msg}")
        print("All users after delete:", get_all_users())

