from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QCheckBox, QWidget
from PySide6.QtCore import Signal, Qt, QThreadPool
from src.db.user_queries import add_user, get_user_details
from src.components.validated_line_edit import ValidatedLineEdit

from src.components.async_worker import Worker

class RegisterDialog(QDialog):
    registration_successful = Signal(str, str) # username, role
    registration_completed = Signal(bool, str, str, str) # success, message, username, role

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("Register")
        self.setFixedSize(400, 450)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(10)

        # Branding/Logo Area
        logo_label = QLabel("Register for ProAuto")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3b82f6;")
        main_layout.addWidget(logo_label)

        def validate_full_name(text):
            if not text.strip():
                return False, "Full name cannot be empty."
            return True, ""

        def validate_email(text):
            if "@" not in text or "." not in text:
                return False, "Invalid email format."
            return True, ""

        def validate_username(text):
            if len(text) < 3:
                return False, "Username must be at least 3 characters."
            return True, ""

        def validate_password(text):
            if len(text) < 6:
                return False, "Password must be at least 6 characters."
            return True, ""

        self.full_name_input = ValidatedLineEdit(placeholder_text="Full Name", validation_func=validate_full_name)
        main_layout.addWidget(self.full_name_input)
        self.full_name_input.validation_changed.connect(self._check_form_validity)

        self.email_input = ValidatedLineEdit(placeholder_text="Email", validation_func=validate_email)
        main_layout.addWidget(self.email_input)
        self.email_input.validation_changed.connect(self._check_form_validity)

        self.username_input = ValidatedLineEdit(placeholder_text="Username", validation_func=validate_username)
        main_layout.addWidget(self.username_input)
        self.username_input.validation_changed.connect(self._check_form_validity)

        self.password_input = ValidatedLineEdit(placeholder_text="Password", validation_func=validate_password)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.line_edit.textChanged.connect(self._update_password_strength)
        main_layout.addWidget(self.password_input)
        self.password_input.validation_changed.connect(self._check_form_validity)

        self.password_strength_label = QLabel("Password Strength: ")
        self.password_strength_label.setStyleSheet("font-size: 10px; color: gray;")
        main_layout.addWidget(self.password_strength_label)

        self.confirm_password_input = ValidatedLineEdit(placeholder_text="Confirm Password", validation_func=lambda text: (text == self.password_input.text(), "Passwords do not match.") if text else (False, "Confirm password cannot be empty."))
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.line_edit.textChanged.connect(lambda: self.confirm_password_input._validate_input(self.confirm_password_input.text())) # Re-validate confirm password when password changes
        main_layout.addWidget(self.confirm_password_input)
        self.confirm_password_input.validation_changed.connect(self._check_form_validity)

        self.terms_checkbox = QCheckBox("I agree to the Terms & Conditions")
        self.terms_checkbox.stateChanged.connect(self._check_form_validity)
        main_layout.addWidget(self.terms_checkbox)

        self.register_button = QPushButton("Register")
        self.register_button.setFixedHeight(40)
        self.register_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.register_button.clicked.connect(self.attempt_register)
        self.register_button.setEnabled(False) # Disable initially
        main_layout.addWidget(self.register_button)

        login_link = QLabel("Already have an account? <a href=\"#\">Login</a>")
        login_link.setAlignment(Qt.AlignCenter)
        login_link.linkActivated.connect(self.reject) # Close register dialog and return to login
        main_layout.addWidget(login_link)

        self.threadpool = QThreadPool.globalInstance()

    def _update_password_strength(self, password):
        strength = 0
        if len(password) > 5: strength += 1
        if any(c.islower() for c in password): strength += 1
        if any(c.isupper() for c in password): strength += 1
        if any(c.isdigit() for c in password): strength += 1
        if any(not c.isalnum() for c in password): strength += 1

        if strength == 0:
            self.password_strength_label.setText("Password Strength: ")
            self.password_strength_label.setStyleSheet("font-size: 10px; color: gray;")
        elif strength < 3:
            self.password_strength_label.setText("Password Strength: Weak")
            self.password_strength_label.setStyleSheet("font-size: 10px; color: red;")
        elif strength < 5:
            self.password_strength_label.setText("Password Strength: Medium")
            self.password_strength_label.setStyleSheet("font-size: 10px; color: orange;")
        else:
            self.password_strength_label.setText("Password Strength: Strong")
            self.password_strength_label.setStyleSheet("font-size: 10px; color: green;")
        
        self.confirm_password_input._validate_input(self.confirm_password_input.text()) # Re-validate confirm password when password changes

    def _check_form_validity(self):
        all_inputs_valid = self.full_name_input.isValid() and \
                           self.email_input.isValid() and \
                           self.username_input.isValid() and \
                           self.password_input.isValid() and \
                           self.confirm_password_input.isValid() and \
                           self.terms_checkbox.isChecked()
        self.register_button.setEnabled(all_inputs_valid)

    def attempt_register(self):
        full_name = self.full_name_input.text()
        email = self.email_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        remember_me = False # Registration doesn't imply remember me

        self.register_button.setEnabled(False)
        self.register_button.setText("Registering...")

        def _register_task(**kwargs): # Accept **kwargs
            import time
            time.sleep(1.5) # Simulate 1.5 seconds delay
            return add_user(username, password, email=email, role='user', avatar=None)

        worker = Worker(_register_task)
        worker.signals.result.connect(lambda result: self._handle_register_result(result, username, password))
        worker.signals.finished.connect(lambda: print("Registration task finished."))
        self.threadpool.start(worker)

    def _handle_register_result(self, result_tuple, username, password):
        success, message = result_tuple
        if success:
            # After successful registration, trigger login and accept this dialog.
            # The parent LoginDialog will handle the result of the async login.
            self.user_manager.login(username, password)
            self.accept()
        else:
            QMessageBox.warning(self, "Registration Failed", message)
            self.register_button.setEnabled(True)
            self.register_button.setText("Register")
