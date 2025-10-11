import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PySide6.QtGui import QFontDatabase
from src.app.layout import MainLayout
from src.styles.theme_manager import ThemeManager
from src.db.user_queries import initialize_db, add_user
from src.auth_dialog import LoginDialog
from src.user_manager import UserManager


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

    # Load custom fonts
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'Sarabun')
    if os.path.exists(fonts_dir):
        for font_file in os.listdir(fonts_dir):
            if font_file.endswith('.ttf'):
                font_path = os.path.join(fonts_dir, font_file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id == -1:
                    print(f"Warning: Failed to load font: {font_path}")
                else:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        print(f"Successfully loaded font: {font_families[0]}")

    load_dotenv()
    initialize_db()

    # Create managers
    user_manager = UserManager()
    theme_manager = ThemeManager(app)
    theme_manager.set_light_theme() # Default to light theme

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
        sys.exit(app.exec()) # Start the event loop and exit when it's done
    else:
        # This case handles if the login was cancelled initially.
        sys.exit(0)


if __name__ == "__main__":
    main()