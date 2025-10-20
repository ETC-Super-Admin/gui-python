import sqlite3
import os

DATABASE_NAME = "app_database.db"

def initialize_db():
    """Initializes the database and creates the unmerged_files table if it doesn't exist."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unmerged_files (
                file_path TEXT PRIMARY KEY,
                unmerged_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_unmerged_file(file_path):
    """Adds a successfully unmerged file path to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO unmerged_files (file_path) VALUES (?)", (file_path,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Path already exists, which is fine.
            return True
        except sqlite3.Error as e:
            print(f"Database error in add_unmerged_file: {e}")
            return False

def is_file_unmerged(file_path):
    """Checks if a file has already been unmerged."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM unmerged_files WHERE file_path = ?", (file_path,))
        return cursor.fetchone() is not None

def clear_unmerged_files_for_day(year: int, month: int, day: int):
    """Deletes all unmerged file records for a specific day."""
    # Construct a path segment that is OS-agnostic for the LIKE query
    path_segment = os.path.join(f"Year_{year:04d}", f"Month_{month:02d}", "Daily_Bills", f"Day_{day}")
    like_pattern = f"%{path_segment}%"

    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM unmerged_files WHERE file_path LIKE ?", (like_pattern,))
            deleted_rows = cursor.rowcount
            conn.commit()
            return True, f"Cleared {deleted_rows} unmerged file records for the selected day."
        except sqlite3.Error as e:
            return False, f"Database error while clearing unmerged cache: {e}"
