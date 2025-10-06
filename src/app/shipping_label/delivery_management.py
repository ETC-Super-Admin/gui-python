from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, 
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, 
    QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt
import qtawesome as qta

from src.db.delivery_by_queries import (
    initialize_delivery_db, get_all_delivery_options, add_delivery_option, 
    update_delivery_option, delete_delivery_option
)
from src.db.config_queries import save_config, get_config

class EditDialog(QDialog):
    """A simple dialog for editing a delivery option name."""
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Option")
        layout = QVBoxLayout(self)
        
        self.label = QLabel(f"Editing: {current_name}")
        layout.addWidget(self.label)
        
        self.line_edit = QLineEdit(current_name)
        layout.addWidget(self.line_edit)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_new_name(self):
        return self.line_edit.text().strip()

class DeliveryManagement(QWidget):
    def __init__(self):
        super().__init__()
        initialize_delivery_db()
        self.setup_ui()
        self.load_options_to_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Delivery Options Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # --- Top section for adding new options ---
        add_layout = QHBoxLayout()
        add_layout.setSpacing(10)
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("Enter new delivery option name...")
        self.add_input.returnPressed.connect(self.add_new_option)
        add_layout.addWidget(self.add_input)
        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Option")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.add_new_option)
        add_layout.addWidget(self.add_button)
        main_layout.addLayout(add_layout)

        # --- Table of existing options ---
        self.options_table = QTableWidget()
        self.options_table.setObjectName("Card")
        self.options_table.setColumnCount(2)
        self.options_table.setHorizontalHeaderLabels(["Default", "Delivery Option Name"])
        header = self.options_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.options_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.options_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.options_table.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.options_table)

        # --- Bottom section for actions on selected item ---
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.set_default_button = QPushButton(qta.icon('fa5s.star', color='white'), " Set as Default")
        self.set_default_button.clicked.connect(self.set_as_default)
        self.set_default_button.setEnabled(False)
        action_layout.addWidget(self.set_default_button)
        self.edit_button = QPushButton(qta.icon('fa5s.edit', color='white'), " Edit Selected")
        self.edit_button.setObjectName("EditUserButton")
        self.edit_button.clicked.connect(self.edit_selected_option)
        self.edit_button.setEnabled(False)
        action_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt', color='white'), " Delete Selected")
        self.delete_button.setObjectName("DeleteUserButton")
        self.delete_button.clicked.connect(self.delete_selected_option)
        self.delete_button.setEnabled(False)
        action_layout.addWidget(self.delete_button)
        main_layout.addLayout(action_layout)

    def load_options_to_table(self):
        self.options_table.setRowCount(0)
        options = get_all_delivery_options()
        default_option = get_config("default_delivery_by")

        for option_name in options:
            row_position = self.options_table.rowCount()
            self.options_table.insertRow(row_position)

            default_item = QTableWidgetItem()
            if option_name == default_option:
                default_item.setText(" ★ ")
                default_item.setTextAlignment(Qt.AlignCenter)
            
            self.options_table.setItem(row_position, 0, default_item)
            self.options_table.setItem(row_position, 1, QTableWidgetItem(option_name))
        
        self.on_selection_changed() # Update button states

    def on_selection_changed(self):
        is_item_selected = bool(self.options_table.selectedItems())
        self.edit_button.setEnabled(is_item_selected)
        self.delete_button.setEnabled(is_item_selected)
        self.set_default_button.setEnabled(is_item_selected)

    def add_new_option(self):
        new_option_name = self.add_input.text().strip()
        if not new_option_name:
            QMessageBox.warning(self, "Input Error", "Option name cannot be empty.")
            return
        
        success, message = add_delivery_option(new_option_name)
        if success:
            self.add_input.clear()
            self.load_options_to_table()
        else:
            QMessageBox.warning(self, "Error", message)

    def edit_selected_option(self):
        selected_items = self.options_table.selectedItems()
        if not selected_items:
            return
        
        old_name = selected_items[0].text()
        dialog = EditDialog(old_name, self)
        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.get_new_name()
            if not new_name:
                QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
                return
            if new_name.lower() == old_name.lower():
                return # No change

            success, message = update_delivery_option(old_name, new_name)
            if success:
                self.load_options_to_table()
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_selected_option(self):
        selected_items = self.options_table.selectedItems()
        if not selected_items:
            return

        name_to_delete = self.options_table.item(selected_items[0].row(), 1).text()
        reply = QMessageBox.question(self, 'Delete Option',
                                     f"Are you sure you want to delete '{name_to_delete}'?\nThis will also update any receivers using this option.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_delivery_option(name_to_delete)
            if success:
                self.load_options_to_table()
            else:
                QMessageBox.warning(self, "Error", message)

    def set_as_default(self):
        selected_items = self.options_table.selectedItems()
        if not selected_items:
            return

        name_to_set = self.options_table.item(selected_items[0].row(), 1).text()
        success, message = save_config("default_delivery_by", name_to_set)
        if success:
            QMessageBox.information(self, "Success", f"'{name_to_set}' has been set as the default.")
            self.load_options_to_table() # Reload to show the new default star
        else:
            QMessageBox.warning(self, "Error", f"Could not set default: {message}")