from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, 
    QFormLayout, QGroupBox, QFileDialog, QMessageBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta

# Import new DB queries for path configs and the global config functions
from src.db.path_config_queries import (
    initialize_path_config_db, add_path_config, get_all_path_configs, 
    update_path_config, delete_path_config
)
from src.db.config_queries import save_config, get_config

class PathConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.current_inventory_code = None # To track which item is being edited
        initialize_path_config_db()
        self.setup_ui()
        self.load_configs_to_table()
        self.clear_form()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Path Configuration Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Layout for Table (left) and Form (right)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- Left Side (Table) ---
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)

        # Header with Title and Add button
        table_header_layout = QHBoxLayout()
        table_title = QLabel("All Path Configurations")
        table_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()
        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add New")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.clear_form)
        table_header_layout.addWidget(self.add_button)
        table_layout.addLayout(table_header_layout)

        self.config_table = QTableWidget()
        self.config_table.setObjectName("Card")
        self.config_table.setAlternatingRowColors(True)
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["Default", "Inventory Code", "Template Directory"])
        header = self.config_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.config_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.config_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.config_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        table_layout.addWidget(self.config_table)

        # --- Right Side (Form) ---
        form_widget = QWidget()
        form_layout_container = QVBoxLayout(form_widget)
        form_layout_container.setContentsMargins(0, 0, 0, 0)
        form_layout_container.setSpacing(15)

        self.form_groupbox = QGroupBox("Manage Configuration")
        self.form_groupbox.setObjectName("Card")
        form_layout = QFormLayout(self.form_groupbox)
        form_layout.setSpacing(10)

        self.inventory_code_input = QLineEdit()
        self.inventory_code_input.setPlaceholderText("e.g., BKK, CNX")
        form_layout.addRow("Inventory Code:", self.inventory_code_input)

        self.template_dir_input = QLineEdit()
        self.template_dir_input.setPlaceholderText("Select the template directory")
        self.template_dir_input.setReadOnly(True)
        browse_button = QPushButton(qta.icon('fa5s.folder-open', color='#64748b'), " Browse...")
        browse_button.setObjectName("CancelFormButton")
        browse_button.clicked.connect(self.browse_template_directory)
        template_dir_layout = QHBoxLayout()
        template_dir_layout.addWidget(self.template_dir_input)
        template_dir_layout.addWidget(browse_button)
        form_layout.addRow("Template Directory:", template_dir_layout)

        # Action buttons for the form
        form_action_layout = QHBoxLayout()
        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save")
        self.save_button.setObjectName("SaveUserButton")
        self.save_button.clicked.connect(self.save_configuration)
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt', color='white'), " Delete")
        self.delete_button.setObjectName("DeleteUserButton")
        self.delete_button.clicked.connect(self.delete_configuration)
        self.set_default_button = QPushButton(qta.icon('fa5s.star', color='white'), " Set as Default")
        self.set_default_button.clicked.connect(self.set_as_default)
        form_action_layout.addStretch()
        form_action_layout.addWidget(self.set_default_button)
        form_action_layout.addWidget(self.delete_button)
        form_action_layout.addWidget(self.save_button)
        form_layout.addRow(form_action_layout)

        form_layout_container.addWidget(self.form_groupbox)
        form_layout_container.addStretch()

        # Add left and right widgets to the main content layout
        content_layout.addWidget(table_widget, 1)
        content_layout.addWidget(form_widget, 1)

        # --- Add Keyboard Shortcut for Saving ---
        shortcut = QShortcut(QKeySequence("Shift+Return"), self)
        shortcut.activated.connect(self.save_configuration)

    def load_configs_to_table(self):
        self.config_table.setRowCount(0)
        configs = get_all_path_configs()
        default_code = get_config("bills_process_inventory_code")

        for config in configs:
            row_position = self.config_table.rowCount()
            self.config_table.insertRow(row_position)

            default_item = QTableWidgetItem()
            if config["inventory_code"] == default_code:
                default_item.setText(" ★ ")
                default_item.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row_position, 0, default_item)

            self.config_table.setItem(row_position, 1, QTableWidgetItem(config["inventory_code"]))
            self.config_table.setItem(row_position, 2, QTableWidgetItem(config["template_dir"]))

    def on_table_selection_changed(self):
        selected_items = self.config_table.selectedItems()
        if not selected_items:
            self.clear_form()
            return

        selected_row = selected_items[0].row()
        inventory_code = self.config_table.item(selected_row, 1).text()
        template_dir = self.config_table.item(selected_row, 2).text()

        self.current_inventory_code = inventory_code
        self.form_groupbox.setTitle(f"Edit '{inventory_code}'")
        self.inventory_code_input.setText(inventory_code)
        self.inventory_code_input.setReadOnly(True) # Cannot edit primary key
        self.template_dir_input.setText(template_dir)

        self.save_button.setText(" Update")
        self.delete_button.setVisible(True)
        self.set_default_button.setVisible(True)

    def clear_form(self):
        self.config_table.clearSelection()
        self.current_inventory_code = None
        self.form_groupbox.setTitle("Add New Configuration")
        self.inventory_code_input.clear()
        self.inventory_code_input.setReadOnly(False)
        self.template_dir_input.clear()
        self.save_button.setText(" Save")
        self.delete_button.setVisible(False)
        self.set_default_button.setVisible(False)
        self.inventory_code_input.setFocus()

    def browse_template_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Template Directory")
        if directory:
            self.template_dir_input.setText(directory)

    def save_configuration(self):
        inventory_code = self.inventory_code_input.text().strip().upper()
        template_dir = self.template_dir_input.text()

        if not inventory_code or not template_dir:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if self.current_inventory_code: # Update existing
            success, message = update_path_config(inventory_code, template_dir)
        else: # Add new
            success, message = add_path_config(inventory_code, template_dir)

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_configs_to_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", message)

    def delete_configuration(self):
        if not self.current_inventory_code:
            return

        reply = QMessageBox.question(self, 'Delete Configuration',
                                     f"Are you sure you want to delete the configuration for '{self.current_inventory_code}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_path_config(self.current_inventory_code)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_configs_to_table()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", message)

    def set_as_default(self):
        if not self.current_inventory_code:
            return
        
        success, message = save_config("bills_process_inventory_code", self.current_inventory_code)
        if success:
            QMessageBox.information(self, "Success", f"'{self.current_inventory_code}' has been set as the default.")
            self.load_configs_to_table() # Reload to show the new default star
        else:
            QMessageBox.warning(self, "Error", f"Could not set default: {message}")
