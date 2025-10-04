import sys
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from src.app.layout import MainLayout
from src.styles.theme_manager import ThemeManager
from src.database import initialize_db, add_user
from src.auth_dialog import LoginDialog
from src.user_manager import UserManager


class MainWindow(QMainWindow):
    def __init__(self, theme_manager, user_manager):
        super().__init__()
        self._is_handling_close = False
        self.user_manager = user_manager
        self.setWindowTitle(f"ProAuto - {self.user_manager.get_username()} ({self.user_manager.get_user_role()})")
        self.setGeometry(100, 100, 1400, 800)

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

    def closeEvent(self, event):
        if self._is_handling_close:
            event.accept()
            return

        self._is_handling_close = True
        self.user_manager.logout() # This will trigger self.close() via the signal
        event.accept() # Accept the original close event

def main():
    app = QApplication(sys.argv)
    load_dotenv()
    initialize_db()

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if admin_username and admin_password:
        success, message = add_user(admin_username, admin_password, email="admin@example.com", role='admin', avatar="admin_avatar.png")
        if success:
            print(f"Admin user '{admin_username}' added to the database.")
        elif "already exists" in message:
            print(f"Admin user '{admin_username}' already exists in the database.")

    user_manager = UserManager()
    theme_manager = ThemeManager(app)
    theme_manager.set_light_theme()

    while True:
        # If user is not logged in (or has just logged out), show login dialog.
        if not user_manager.is_logged_in():
            login_dialog = LoginDialog(user_manager=user_manager)
            if login_dialog.exec() != QDialog.Accepted:
                # User cancelled login, so exit the application loop.
                break
        
        # If login was successful, proceed to show the main window.
        if user_manager.is_logged_in():
            main_window = MainWindow(theme_manager, user_manager)
            main_window.show()
            app.exec() # This will block until MainWindow is closed (on logout).
            # After window is closed, the loop continues, and the user will be logged out.
        else:
            # This case is reached if the very first login is cancelled.
            break

    sys.exit(0)


if __name__ == "__main__":
    main()