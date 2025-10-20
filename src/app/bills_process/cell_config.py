from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt
import qtawesome as qta

# Import DB queries for bill configs
from src.db.bill_config_queries import (
    initialize_bill_config_db, add_bill_config, get_all_bill_configs,
    update_bill_config, delete_bill_config
)

class CellConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.current_config_id = None
        self.config_types = ["By Cell", "By Column"]
        initialize_bill_config_db()
        self.setup_ui()
        self.load_configs_to_table()
        self.clear_form()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Bill Processing Configuration")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- Left Side (Table) ---
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)

        table_header_layout = QHBoxLayout()
        table_title = QLabel("All Configurations")
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
        self.config_table.setColumnCount(6)
        self.config_table.setHorizontalHeaderLabels(["ID", "Field Name", "Type", "Focus", "Check", "Value"])
        header = self.config_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Field Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Focus
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Check
        header.setSectionResizeMode(5, QHeaderView.Stretch) # Value
        self.config_table.setColumnHidden(0, True)
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
        self.form_layout = QVBoxLayout(self.form_groupbox)
        self.form_layout.setSpacing(8)

        # Field Name
        self.form_layout.addWidget(QLabel("Field Name:"))
        self.field_name_input = QLineEdit()
        self.field_name_input.setPlaceholderText("e.g., invoice_number, total_amount")
        self.form_layout.addWidget(self.field_name_input)

        # Config Type
        self.form_layout.addWidget(QLabel("Config Type:"))
        self.config_type_combo = QComboBox()
        self.config_type_combo.addItems(self.config_types)
        self.config_type_combo.currentTextChanged.connect(self.on_config_type_changed)
        self.form_layout.addWidget(self.config_type_combo)

        # Focus
        self.focus_label = QLabel("Focus Cell:")
        self.form_layout.addWidget(self.focus_label)
        self.focus_input = QLineEdit()
        self.form_layout.addWidget(self.focus_input)

        # Check
        self.check_label = QLabel("Check Cell:")
        self.form_layout.addWidget(self.check_label)
        self.check_input = QLineEdit()
        self.form_layout.addWidget(self.check_input)

        # Value
        self.value_label = QLabel("Check Value:")
        self.form_layout.addWidget(self.value_label)
        self.value_input = QLineEdit()
        self.form_layout.addWidget(self.value_input)

        self.form_layout.addStretch(1)

        # Action Buttons
        form_action_layout = QHBoxLayout()
        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save")
        self.save_button.setObjectName("SaveUserButton")
        self.save_button.clicked.connect(self.save_configuration)
        
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt', color='white'), " Delete")
        self.delete_button.setObjectName("DeleteUserButton")
        self.delete_button.clicked.connect(self.delete_configuration)

        self.cancel_button = QPushButton(qta.icon('fa5s.times', color='#64748b'), " Cancel")
        self.cancel_button.setObjectName("CancelFormButton")
        self.cancel_button.clicked.connect(self.clear_form)

        form_action_layout.addStretch()
        form_action_layout.addWidget(self.cancel_button)
        form_action_layout.addWidget(self.delete_button)
        form_action_layout.addWidget(self.save_button)
        self.form_layout.addLayout(form_action_layout)

        form_layout_container.addWidget(self.form_groupbox)
        form_layout_container.addStretch()

        content_layout.addWidget(table_widget, 2)
        content_layout.addWidget(form_widget, 1)

        self.on_config_type_changed(self.config_types[0])

    def on_config_type_changed(self, config_type):
        if config_type == "By Cell":
            self.focus_label.setText("Focus Cell:")
            self.focus_input.setPlaceholderText("e.g., B2")
            self.check_label.setText("Check Cell:")
            self.check_input.setPlaceholderText("e.g., A2")
            self.value_label.setText("Check Value:")
            self.value_input.setPlaceholderText("e.g., Invoice No")
            self.check_label.show()
            self.check_input.show()
        elif config_type == "By Column":
            self.focus_label.setText("Focus Column:")
            self.focus_input.setPlaceholderText("e.g., A")
            self.check_label.setText("Check Focus Value:")
            self.check_input.setPlaceholderText("e.g., Total")
            self.value_label.setText("Collect Column:")
            self.value_input.setPlaceholderText("e.g., B")
            self.check_label.show()
            self.check_input.show()

    def load_configs_to_table(self):
        self.config_table.setRowCount(0)
        configs = get_all_bill_configs()
        for config in configs:
            row_position = self.config_table.rowCount()
            self.config_table.insertRow(row_position)
            self.config_table.setItem(row_position, 0, QTableWidgetItem(str(config["id"])))
            self.config_table.setItem(row_position, 1, QTableWidgetItem(config["field_name"]))
            self.config_table.setItem(row_position, 2, QTableWidgetItem(self.config_types[config["config_type"]]))
            self.config_table.setItem(row_position, 3, QTableWidgetItem(config["focus"]))
            self.config_table.setItem(row_position, 4, QTableWidgetItem(config.get("check_text", "")))
            self.config_table.setItem(row_position, 5, QTableWidgetItem(config.get("value", "")))

    def on_table_selection_changed(self):
        selected_items = self.config_table.selectedItems()
        if not selected_items:
            self.clear_form()
            return

        selected_row = selected_items[0].row()
        config_id = self.config_table.item(selected_row, 0).text()
        
        configs = get_all_bill_configs()
        config = next((c for c in configs if c['id'] == int(config_id)), None)

        if not config:
            self.clear_form()
            return

        self.current_config_id = config["id"]
        self.form_groupbox.setTitle(f"Edit '{config['field_name']}'")
        
        self.field_name_input.setText(config["field_name"])
        self.config_type_combo.setCurrentIndex(config["config_type"])
        self.focus_input.setText(config["focus"])
        self.check_input.setText(config.get("check_text", ""))
        self.value_input.setText(config.get("value", ""))

        self.save_button.setText(" Update")
        self.delete_button.setVisible(True)
        self.cancel_button.setVisible(True)

    def clear_form(self):
        self.config_table.clearSelection()
        self.current_config_id = None
        self.form_groupbox.setTitle("Add New Configuration")
        self.field_name_input.clear()
        self.config_type_combo.setCurrentIndex(0)
        self.focus_input.clear()
        self.check_input.clear()
        self.value_input.clear()
        self.save_button.setText(" Save")
        self.delete_button.setVisible(False)
        self.cancel_button.setVisible(False)
        self.field_name_input.setFocus()

    def save_configuration(self):
        field_name = self.field_name_input.text().strip()
        config_type_index = self.config_type_combo.currentIndex()
        config_type = self.config_type_combo.currentText()
        focus = self.focus_input.text().strip()

        if config_type == "By Column":
            check = self.check_input.text()
        else:
            check = self.check_input.text().strip()

        value = self.value_input.text()

        if not field_name or not focus:
            QMessageBox.warning(self, "Input Error", "Field Name and Focus are required.")
            return

        data = {
            "field_name": field_name,
            "config_type": config_type_index,
            "focus": focus,
            "check": check,
            "value": value
        }

        if self.current_config_id:
            success, message = update_bill_config(self.current_config_id, data)
        else:
            success, message = add_bill_config(data)

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_configs_to_table()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", message)

    def delete_configuration(self):
        if not self.current_config_id:
            return

        reply = QMessageBox.question(self, 'Delete Configuration',
                                     "Are you sure you want to delete this configuration?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_bill_config(self.current_config_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_configs_to_table()
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", message)

    def showEvent(self, event):
        super().showEvent(event)
        if self.isVisible():
            self.load_configs_to_table()