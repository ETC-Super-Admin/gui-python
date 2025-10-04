from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QCheckBox, QWidget
from PySide6.QtCore import Signal, Qt
from src.database import verify_user, get_user_role
from src.register_dialog import RegisterDialog
from src.components.validated_line_edit import ValidatedLineEdit

from src.user_manager import AuthResult

class LoginDialog(QDialog):
    login_successful = Signal(str, str) # username, role

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setObjectName("LoginDialog") # Add object name for styling
        self.setWindowTitle("Login")
        self.setFixedSize(380, 420) # Increase size for better spacing

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30) # Add padding
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)

        # Branding/Logo Area
        logo_label = QLabel("ProAuto")
        logo_label.setObjectName("LoginLogo") # Object name for logo
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #3b82f6;") # Larger font
        main_layout.addWidget(logo_label)

        # Spacer after logo
        main_layout.addSpacing(20)

        def validate_username(text):
            if len(text) < 3:
                return False, "Username must be at least 3 characters."
            return True, ""

        def validate_password(text):
            if len(text) < 6:
                return False, "Password must be at least 6 characters."
            return True, ""

        self.username_input = ValidatedLineEdit(placeholder_text="Username", validation_func=validate_username)
        self.username_input.setObjectName("LoginInput")
        self.username_input.line_edit.returnPressed.connect(self._on_return_pressed)
        main_layout.addWidget(self.username_input)

        self.toggle_password_visibility_button = QPushButton("Show")
        self.toggle_password_visibility_button.setObjectName("LoginTogglePasswordButton")
        self.toggle_password_visibility_button.setCheckable(True)
        self.toggle_password_visibility_button.setFixedSize(60, 35) # Wider button
        self.toggle_password_visibility_button.clicked.connect(self._toggle_password_visibility)

        self.password_input = ValidatedLineEdit(placeholder_text="Password", validation_func=validate_password, echo_mode=QLineEdit.Password, toggle_button=self.toggle_password_visibility_button)
        self.password_input.setObjectName("LoginInput")
        self.password_input.line_edit.returnPressed.connect(self._on_return_pressed)
        main_layout.addWidget(self.password_input)
        self.password_input.validation_changed.connect(self._check_form_validity)
        
        options_layout = QHBoxLayout()
        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setObjectName("LoginCheckbox")
        options_layout.addWidget(self.remember_me_checkbox)
        options_layout.addStretch()
        forgot_password_link = QLabel("<a href=\"#\">Forgot password?</a>")
        forgot_password_link.setObjectName("LoginLink")
        forgot_password_link.linkActivated.connect(self._forgot_password)
        options_layout.addWidget(forgot_password_link)
        main_layout.addLayout(options_layout)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("LoginButton")
        self.login_button.setFixedHeight(45) # Taller button
        self.login_button.setStyleSheet("font-size: 18px; font-weight: bold;") # Larger font
        self.login_button.clicked.connect(self.attempt_login)
        main_layout.addWidget(self.login_button)
        self.login_button.setEnabled(False) # Disable initially

        main_layout.addSpacing(15) # Spacer before create account link

        create_account_link = QLabel("Don't have an account? <a href=\"#\">Create one</a>")
        create_account_link.setObjectName("LoginLink")
        create_account_link.setAlignment(Qt.AlignCenter)
        create_account_link.linkActivated.connect(self._create_account)
        main_layout.addWidget(create_account_link)

        # Connect to UserManager's login_completed signal
        self.user_manager.login_completed.connect(self._handle_login_result)

    def _check_form_validity(self):
        self.login_button.setEnabled(self.username_input.isValid() and self.password_input.isValid())

    def _on_return_pressed(self):
        if self.login_button.isEnabled():
            self.attempt_login()

    def _toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_visibility_button.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_visibility_button.setText("Show")

    def _forgot_password(self):
        QMessageBox.information(self, "Forgot Password", "This feature is not yet implemented. Please contact support.")

    def _create_account(self):
        register_dialog = RegisterDialog(user_manager=self.user_manager, parent=self)
        if register_dialog.exec() == QDialog.Accepted:
            # If registration was successful, RegisterDialog will have triggered an
            # asynchronous login. This LoginDialog is already connected to the
            # user_manager.login_completed signal, so it will close itself
            # automatically upon successful login. No further action is needed here.
            pass

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        remember_me = self.remember_me_checkbox.isChecked()

        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")

        self.user_manager.login(username, password, remember_me) # Call asynchronous login

    def _handle_login_result(self, result, username, role):
        if result == AuthResult.SUCCESS:
            self.login_successful.emit(username, role)
            self.accept() # Close dialog with accept result
        else:
            error_message = "An unknown error occurred."
            if result == AuthResult.INVALID_CREDENTIALS:
                error_message = "Invalid username or password."
            elif result == AuthResult.UNAUTHORIZED:
                error_message = "Authentication failed. Please check your credentials."
            elif result == AuthResult.FORBIDDEN:
                error_message = "Access denied. You do not have permission."
            elif result == AuthResult.SERVER_ERROR:
                error_message = "Server error. Please try again later."
            
            QMessageBox.warning(self, "Login Failed", error_message)
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")

    def done(self, result):
        # Disconnect the signal to prevent issues on re-login or leaks
        try:
            self.user_manager.login_completed.disconnect(self._handle_login_result)
        except (TypeError, RuntimeError):
            pass
        super().done(result)
