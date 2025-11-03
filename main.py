import sys
import os
import shutil
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PySide6.QtGui import QFontDatabase, QFont
from src.app.layout import MainLayout
from src.styles.theme_manager import ThemeManager
from src.db.user_queries import initialize_db, add_user
from src.db.unmerged_files_queries import initialize_db as initialize_unmerged_db
from src.db import (
    address_queries,
    bill_config_queries,
    config_queries,
    delivery_by_queries,
    path_config_queries,
    receiver_queries,
    sender_queries,
)
from src.auth_dialog import LoginDialog
from src.user_manager import UserManager
from src.styles.custom_style import NoFocusProxyStyle
import sqlite3
from import_tambons import import_data as import_address_data



def ensure_thai_addresses_table_exists(db_path):
    """Checks if the thai_addresses table exists and imports data if it doesn't."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM thai_addresses LIMIT 1")
    except sqlite3.OperationalError:
        print("`thai_addresses` table not found, importing from `tambons.sql`...")
        import_address_data(db_path)


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Used for read-only bundled resources like .env files.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_writable_path(filename):
    """
    Get path for writable files (like databases).
    Returns the directory where the executable is located (if frozen)
    or the script directory (if running as script).
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # Use the directory where the executable is located
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, filename)


class MainWindow(QMainWindow):
    def __init__(self, theme_manager, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setWindowTitle(f"ProAuto - {self.user_manager.get_username()} ({self.user_manager.get_user_role()})")
        self.setGeometry(100, 100, 1400, 860)

        self.main_layout_widget = MainLayout(theme_manager, self.user_manager.get_username(), self.user_manager.get_user_role())
        self.main_layout_widget.navbar.logout_requested.connect(self.user_manager.logout)
        
        # If re-authentication is requested (e.g. by trying to access a protected page),
        # just log out. The main loop will handle showing the login dialog again.
        self.main_layout_widget.reauthenticate_requested.connect(self.user_manager.logout)
        
        self.user_manager.user_logged_out.connect(self.close)
        self.setCentralWidget(self.main_layout_widget)

        # Navigate to intended destination if set from a previous session
        if self.user_manager.intended_destination:
            self.main_layout_widget.switch_page(self.user_manager.intended_destination)
            self.user_manager.intended_destination = None

def main():
    app = QApplication(sys.argv)
    app.setStyle(NoFocusProxyStyle())

    app.setFont(QFont("Tahoma", 10))

    # Load .env file from bundled resources (read-only)
    env_path = get_resource_path('.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Fallback: try loading from current directory
        load_dotenv()
    
    # Get writable path for the database.
    writable_db_path = get_writable_path('app_database.db')

    # On first run, copy a bundled "master" database if it exists.
    if not os.path.exists(writable_db_path):
        print(f"Database not found at {writable_db_path}. Checking for a bundled database.")
        bundled_db_path = get_resource_path('app_database.db')
        
        if os.path.exists(bundled_db_path) and os.path.abspath(bundled_db_path) != os.path.abspath(writable_db_path):
            print(f"Found bundled database at {bundled_db_path}. Copying to writable location...")
            try:
                # Ensure the destination directory exists.
                os.makedirs(os.path.dirname(writable_db_path), exist_ok=True)
                shutil.copy2(bundled_db_path, writable_db_path)
                print("Database copied successfully.")
            except Exception as e:
                print(f"FATAL: Could not copy database: {e}")
                # In a real GUI app, you'd show a QMessageBox here.
                sys.exit(1)
        else:
            print("No bundled database found. A new empty database will be created on initialization.")

    # Use the writable path for all database operations.
    main_db_path = writable_db_path
    
    # This check remains as a fallback for development or if the bundled DB is missing the table.
    ensure_thai_addresses_table_exists(main_db_path)
    
    # Initialize all database modules with the correct path
    initialize_db(main_db_path)
    initialize_unmerged_db(main_db_path)
    address_queries.set_database_path(main_db_path)
    bill_config_queries.initialize_bill_config_db(main_db_path)
    config_queries.initialize_config_db(main_db_path)
    delivery_by_queries.initialize_delivery_db(main_db_path)
    path_config_queries.initialize_path_config_db(main_db_path)
    receiver_queries.initialize_receiver_db(main_db_path)
    sender_queries.initialize_sender_db(main_db_path)

    # Create managers
    user_manager = UserManager()
    theme_manager = ThemeManager(app)
    theme_manager.set_light_theme()  # Default to light theme

    # Seed admin user from .env if available
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if admin_username and admin_password:
        success, message = add_user(admin_username, admin_password, email="admin@example.com", role='admin', avatar="admin_avatar.png")
        if success:
            print(f"Admin user '{admin_username}' added to the database.")
        elif "already exists" in message:
            print(f"Admin user '{admin_username}' already exists in the database.")

    # Check if a session is already active
    if not user_manager.is_logged_in():
        # If not logged in, show the login dialog
        login_dialog = LoginDialog(user_manager=user_manager)
        if login_dialog.exec() != QDialog.Accepted:
            # If the user cancels the login, exit the application
            sys.exit(0)
        
        # Process pending events to ensure the user state is updated from the login thread
        QApplication.processEvents()
    
    # If we reach here, the user is successfully logged in (either from a saved session or the dialog)
    if user_manager.is_logged_in():
        main_window = MainWindow(theme_manager, user_manager)
        main_window.show()
        sys.exit(app.exec())  # Start the event loop and exit when it's done
    else:
        # This case handles if the login was cancelled initially.
        sys.exit(0)


if __name__ == "__main__":
    main()