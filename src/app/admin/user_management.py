from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QGroupBox, QFormLayout, QLineEdit, QComboBox, QMessageBox
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
from src.components.validated_line_edit import ValidatedLineEdit

from src.database import get_user_details, add_user, verify_user, get_user_role, get_all_users, update_user, delete_user # Assuming these are available for CRUD

class UserManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_user_id = None # To track user being edited
        self.setup_ui()
        self.load_users()
        self.clear_form()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 4, 20, 4)
        main_layout.setSpacing(15)

        # Page Title
        title_label = QLabel("User Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Action Buttons
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.setSpacing(10)

        self.add_user_button = QPushButton(qta.icon('fa5s.user-plus', color='white'), " Add User")
        self.add_user_button.setObjectName("AddUserButton")
        self.add_user_button.clicked.connect(self.show_add_user_form)
        top_buttons_layout.addWidget(self.add_user_button)

        self.edit_user_button = QPushButton(qta.icon('fa5s.user-edit', color='white'), " Edit User")
        self.edit_user_button.setObjectName("EditUserButton")
        self.edit_user_button.clicked.connect(self.show_edit_user_form)
        self.edit_user_button.setEnabled(False) # Disabled until a user is selected
        top_buttons_layout.addWidget(self.edit_user_button)

        self.delete_user_button = QPushButton(qta.icon('fa5s.user-minus', color='white'), " Delete User")
        self.delete_user_button.setObjectName("DeleteUserButton")
        self.delete_user_button.clicked.connect(self.delete_selected_user)
        self.delete_user_button.setEnabled(False) # Disabled until a user is selected
        top_buttons_layout.addWidget(self.delete_user_button)

        top_buttons_layout.addStretch()
        main_layout.addLayout(top_buttons_layout)

        # User Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4) # ID, Username, Email, Role
        self.user_table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Role"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.user_table.itemSelectionChanged.connect(self.on_user_selection_changed)
        self.user_table.setColumnHidden(0, True) # Hide the ID column
        main_layout.addWidget(self.user_table)

        # User Details Form (Add/Edit)
        self.user_form_groupbox = QGroupBox("User Details")
        self.user_form_groupbox.setObjectName("Card")
        self.user_form_groupbox.setVisible(False) # Hidden by default
        
        form_layout = QFormLayout(self.user_form_groupbox)
        form_layout.setContentsMargins(20, 4, 20, 4)
        form_layout.setSpacing(10)

        self.username_input = ValidatedLineEdit(placeholder_text="Username", validation_func=self._validate_username_input)
        form_layout.addRow("Username:", self.username_input)

        self.email_input = ValidatedLineEdit(placeholder_text="Email", validation_func=self._validate_email_input)
        form_layout.addRow("Email:", self.email_input)

        self.password_input = ValidatedLineEdit(placeholder_text="Password (leave blank to keep current)", validation_func=self._validate_password_input)
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        form_layout.addRow("Role:", self.role_combo)

        form_action_buttons_layout = QHBoxLayout()
        self.save_user_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save")
        self.save_user_button.setObjectName("SaveUserButton")
        self.save_user_button.clicked.connect(self.save_user)
        form_action_buttons_layout.addWidget(self.save_user_button)

        self.cancel_form_button = QPushButton(qta.icon('fa5s.times', color='#64748b'), " Cancel")
        self.cancel_form_button.setObjectName("CancelFormButton")
        self.cancel_form_button.clicked.connect(self.clear_form)
        form_action_buttons_layout.addWidget(self.cancel_form_button)
        form_action_buttons_layout.addStretch()

        form_layout.addRow(form_action_buttons_layout)
        main_layout.addWidget(self.user_form_groupbox)

        main_layout.addStretch()

    def _validate_username_input(self, text):
        if len(text) < 3:
            return False, "Username must be at least 3 characters."
        # Add more complex validation if needed (e.g., check uniqueness)
        return True, ""

    def _validate_email_input(self, text):
        if "@" not in text or "." not in text:
            return False, "Invalid email format."
        return True, ""

    def _validate_password_input(self, text):
        if self.current_user_id is None: # Only require password for new users
            if len(text) < 6:
                return False, "Password must be at least 6 characters."
        return True, ""

    def load_users(self):
        self.user_table.setRowCount(0)
        users = get_all_users()
        for user in users:
            self.add_user_to_table(user["id"], user["username"], user["email"], user["role"])

    def add_user_to_table(self, user_id, username, email, role):
        row_position = self.user_table.rowCount()
        self.user_table.insertRow(row_position)
        self.user_table.setItem(row_position, 0, QTableWidgetItem(str(user_id)))
        self.user_table.setItem(row_position, 1, QTableWidgetItem(username))
        self.user_table.setItem(row_position, 2, QTableWidgetItem(email))
        self.user_table.setItem(row_position, 3, QTableWidgetItem(role))

    def on_user_selection_changed(self):
        selected_items = self.user_table.selectedItems()
        if selected_items:
            self.edit_user_button.setEnabled(True)
            self.delete_user_button.setEnabled(True)
        else:
            self.edit_user_button.setEnabled(False)
            self.delete_user_button.setEnabled(False)

    def show_add_user_form(self):
        self.current_user_id = None
        self.user_form_groupbox.setTitle("Add New User")
        self.clear_form()
        self.password_input.setPlaceholderText("Password (required)")
        self.user_form_groupbox.setVisible(True)

    def show_edit_user_form(self):
        selected_items = self.user_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        self.current_user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        email = self.user_table.item(row, 2).text()
        role = self.user_table.item(row, 3).text()

        self.user_form_groupbox.setTitle(f"Edit User: {username}")
        self.username_input.line_edit.setText(username)
        self.email_input.line_edit.setText(email)
        self.password_input.setPlaceholderText("Password (leave blank to keep current)")
        self.role_combo.setCurrentText(role)
        self.user_form_groupbox.setVisible(True)

    def save_user(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not self.username_input.isValid() or not self.email_input.isValid() or (self.current_user_id is None and not self.password_input.isValid()):
            return

        if self.current_user_id is None: # Add new user
            success, message = add_user(username, password, email, role)
            if success:
                self.load_users()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Add User Failed", message)
        else: # Edit existing user
            update_params = {
                "user_id": self.current_user_id,
                "username": username,
                "email": email,
                "role": role
            }
            if password: # Only update password if provided
                update_params["password"] = password
            
            success, message = update_user(**update_params)
            if success:
                self.load_users()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Update User Failed", message)

    def delete_selected_user(self):
        selected_items = self.user_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()

        reply = QMessageBox.question(self, 'Delete User', f"Are you sure you want to delete user '{username}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_user(user_id)
            if success:
                QMessageBox.information(self, "User Deleted", message)
                self.load_users()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Delete User Failed", message)

    def clear_form(self):
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.password_input.setPlaceholderText("Password (leave blank to keep current)")
        self.role_combo.setCurrentIndex(0) # Default to 'user'
        self.user_form_groupbox.setVisible(False)
        self.user_table.clearSelection()
        self.edit_user_button.setEnabled(False)
        self.delete_user_button.setEnabled(False)
