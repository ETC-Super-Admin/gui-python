from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QComboBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta

# Database imports
from src.db.sender_queries import (
    initialize_sender_db, add_sender, get_all_senders, update_sender, 
    delete_sender
)
from src.db.address_queries import get_provinces, get_districts, get_sub_districts, get_zipcode, get_addresses_by_zipcode
from src.db.config_queries import get_config
from src.db.path_config_queries import get_all_path_configs
from src.components.validated_line_edit import ValidatedLineEdit

class SenderManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_sender_id = None
        initialize_sender_db()
        self.setup_ui()
        self.load_senders_to_table() # This will also populate the dropdown
        self.initialize_address_dropdowns()
        self.show_add_form()

    def showEvent(self, event):
        """Override showEvent to refresh data when the widget is shown."""
        super().showEvent(event)
        if self.isVisible():
            self.load_senders_to_table()


    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Sender Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- Left Side --- 
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        table_header_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Search by Name", "Search by Tel.", "Search by Inventory", "Search by Province",
            "Search by District", "Search by Sub-district", "Search by Post Code"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        table_header_layout.addWidget(self.filter_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search table...")
        self.search_input.textChanged.connect(self.filter_table)
        table_header_layout.addWidget(self.search_input)

        table_header_layout.addStretch()

        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Sender")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.show_add_form)
        table_header_layout.addWidget(self.add_button)
        
        left_layout.addLayout(table_header_layout)

        self.sender_table = QTableWidget()
        self.sender_table.setObjectName("Card")
        self.sender_table.setAlternatingRowColors(True) # Enable striped rows
        self.sender_table.setColumnCount(9)
        self.sender_table.setHorizontalHeaderLabels([
            "ID", "Inventory", "Name", "Address Details", "Sub-district",
            "District", "Province", "Post Code", "Tel."
        ])
        header = self.sender_table.horizontalHeader()
        header.setMinimumSectionSize(120)

        # Set Name to stretch
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Set other columns to be interactive with default widths
        for i in range(self.sender_table.columnCount()):
            if i not in [0, 2]: # Skip ID and Name
                header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        self.sender_table.setColumnWidth(1, 120) # Inventory
        self.sender_table.setColumnWidth(3, 250) # Address Details
        self.sender_table.setColumnWidth(4, 150) # Sub-district
        self.sender_table.setColumnWidth(5, 150) # District
        self.sender_table.setColumnWidth(6, 150) # Province
        self.sender_table.setColumnWidth(7, 100) # Post Code
        self.sender_table.setColumnWidth(8, 120) # Tel

        self.sender_table.setColumnHidden(0, True) # Hide ID column

        self.sender_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sender_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sender_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.sender_table.itemSelectionChanged.connect(self.on_sender_selection_changed)
        left_layout.addWidget(self.sender_table)

        # --- Right Side --- 
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        self.form_groupbox = QGroupBox("Manage Sender")
        self.form_groupbox.setObjectName("Card")
        form_layout = QFormLayout(self.form_groupbox)
        form_layout.setSpacing(10)

        self.inventory_combo = QComboBox()
        form_layout.addRow("Inventory:", self.inventory_combo)

        self.name_input = ValidatedLineEdit(
            placeholder_text="Enter sender's name",
            validation_func=lambda text: (len(text.strip()) >= 3, "Name must be at least 3 characters."),
            validation_mode='on_demand'
        )
        form_layout.addRow("Name:", self.name_input)

        # --- New Address Fields ---
        self.postcode_input = QLineEdit()
        self.postcode_input.setPlaceholderText("Enter 5-digit post code")
        self.postcode_input.returnPressed.connect(self.on_find_by_zipcode_clicked)
        find_zip_button = QPushButton(qta.icon('fa5s.search', color='white'), " Find")
        find_zip_button.clicked.connect(self.on_find_by_zipcode_clicked)
        
        postcode_layout = QHBoxLayout()
        postcode_layout.addWidget(self.postcode_input)
        postcode_layout.addWidget(find_zip_button)
        form_layout.addRow("Post Code Lookup:", postcode_layout)

        self.province_combo = QComboBox()
        self.district_combo = QComboBox()
        self.sub_district_combo = QComboBox()
        form_layout.addRow("Province:", self.province_combo)
        form_layout.addRow("District:", self.district_combo)
        form_layout.addRow("Sub-district:", self.sub_district_combo)

        self.address_detail_input = ValidatedLineEdit(
            placeholder_text="House No., Street, etc.",
            validation_func=lambda text: (text.strip() != "", "Address details cannot be empty."),
            validation_mode='on_demand'
        )
        form_layout.addRow("Address Details:", self.address_detail_input)
        # --- End New Address Fields ---

        self.tel_input = ValidatedLineEdit(
            placeholder_text="Enter tel. numbers, separated by commas",
            validation_func=lambda text: (text.strip() != "", "Tel. cannot be empty."),
            validation_mode='on_demand'
        )
        form_layout.addRow("Tel.:", self.tel_input)

        form_action_layout = QHBoxLayout()
        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save")
        self.save_button.setObjectName("SaveUserButton")
        self.save_button.clicked.connect(self.save_sender)
        
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt', color='white'), " Delete")
        self.delete_button.setObjectName("DeleteUserButton")
        self.delete_button.clicked.connect(self.delete_selected_sender)
        self.delete_button.setVisible(False)

        form_action_layout.addStretch()
        form_action_layout.addWidget(self.delete_button)
        form_action_layout.addWidget(self.save_button)
        form_layout.addRow(form_action_layout)

        right_layout.addWidget(self.form_groupbox)
        right_layout.addStretch()

        content_layout.addWidget(left_widget, 7)
        content_layout.addWidget(right_widget, 3)

        # --- Connect Signals for Address Dropdowns ---
        self.province_combo.currentTextChanged.connect(self.on_province_changed)
        self.district_combo.currentTextChanged.connect(self.on_district_changed)
        self.sub_district_combo.currentTextChanged.connect(self.on_sub_district_changed)

        # --- Add Keyboard Shortcut for Saving ---
        shortcut = QShortcut(QKeySequence("Shift+Return"), self)
        shortcut.activated.connect(self.save_sender)

    def filter_table(self):
        filter_column_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()

        column_map = {
            "Search by Name": 2,
            "Search by Tel.": 8,
            "Search by Inventory": 1,
            "Search by Province": 6,
            "Search by District": 5,
            "Search by Sub-district": 4,
            "Search by Post Code": 7
        }
        filter_column_index = column_map.get(filter_column_text)

        if filter_column_index is None:
            return

        for row in range(self.sender_table.rowCount()):
            item = self.sender_table.item(row, filter_column_index)
            if item:
                cell_text = item.text().lower()
                match = search_text in cell_text
                self.sender_table.setRowHidden(row, not match)
            else:
                self.sender_table.setRowHidden(row, True)

    def populate_inventory_dropdown(self):
        """
        Fetches inventory codes from the central path configurations, populates the dropdown, 
        and sets the default value.
        """
        self.inventory_combo.blockSignals(True)
        self.inventory_combo.clear()
        
        path_configs = get_all_path_configs()
        codes = sorted([config['inventory_code'] for config in path_configs])
        
        default_code = get_config("bills_process_inventory_code")
        
        if default_code and default_code not in codes:
            codes.append(default_code)
            codes.sort()

        if codes:
            self.inventory_combo.addItems(codes)
        
        if default_code and default_code in codes:
            self.inventory_combo.setCurrentText(default_code)

        self.inventory_combo.blockSignals(False)

    def initialize_address_dropdowns(self):
        self.province_combo.blockSignals(True)
        self.province_combo.clear()
        self.province_combo.addItem("Select Province...")
        provinces = get_provinces()
        if provinces:
            self.province_combo.addItems(provinces)
        self.province_combo.blockSignals(False)
        self.district_combo.setEnabled(False)
        self.sub_district_combo.setEnabled(False)

    def on_province_changed(self, province):
        self.district_combo.blockSignals(True)
        self.district_combo.clear()
        self.district_combo.addItem("Select District...")
        self.sub_district_combo.clear()
        self.postcode_input.clear()

        if province and province != "Select Province...":
            districts = get_districts(province)
            if districts:
                self.district_combo.addItems(districts)
                self.district_combo.setEnabled(True)
        else:
            self.district_combo.setEnabled(False)
        
        self.sub_district_combo.setEnabled(False)
        self.district_combo.blockSignals(False)

    def on_district_changed(self, district):
        self.sub_district_combo.blockSignals(True)
        self.sub_district_combo.clear()
        self.sub_district_combo.addItem("Select Sub-district...")
        self.postcode_input.clear()

        province = self.province_combo.currentText()
        if district and district != "Select District...":
            sub_districts = get_sub_districts(province, district)
            if sub_districts:
                self.sub_district_combo.addItems(sub_districts)
                self.sub_district_combo.setEnabled(True)
        else:
            self.sub_district_combo.setEnabled(False)
        self.sub_district_combo.blockSignals(False)

    def on_sub_district_changed(self, sub_district):
        province = self.province_combo.currentText()
        district = self.district_combo.currentText()
        if sub_district and sub_district != "Select Sub-district...":
            zipcode = get_zipcode(province, district, sub_district)
            self.postcode_input.setText(zipcode)
        else:
            self.postcode_input.clear()

    def on_find_by_zipcode_clicked(self):
        zipcode = self.postcode_input.text()
        if not zipcode or not zipcode.isdigit() or len(zipcode) != 5:
            QMessageBox.warning(self, "Invalid Postcode", "Please enter a valid 5-digit postcode.")
            return

        results = get_addresses_by_zipcode(zipcode)
        if not results:
            QMessageBox.information(self, "Not Found", f"No address data found for postcode {zipcode}.")
            return

        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.sub_district_combo.blockSignals(True)

        province = results[0]['province']
        self.province_combo.setCurrentText(province)

        districts = sorted(list(set(row['district'] for row in results)))
        self.district_combo.clear()
        self.district_combo.addItems(districts)
        self.district_combo.setEnabled(True)

        sub_districts = sorted(list(set(row['sub_district'] for row in results)))
        self.sub_district_combo.clear()
        self.sub_district_combo.addItems(sub_districts)
        self.sub_district_combo.setEnabled(True)

        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.sub_district_combo.blockSignals(False)

        if len(districts) == 1:
            self.district_combo.setCurrentText(districts[0])
        if len(sub_districts) == 1:
            self.sub_district_combo.setCurrentText(sub_districts[0])

    def load_senders_to_table(self):
        self.sender_table.setRowCount(0)
        senders = get_all_senders()
        for sender in senders:
            row_position = self.sender_table.rowCount()
            self.sender_table.insertRow(row_position)
            self.sender_table.setItem(row_position, 0, QTableWidgetItem(str(sender["id"])))
            self.sender_table.setItem(row_position, 1, QTableWidgetItem(sender["inventory_code"]))
            self.sender_table.setItem(row_position, 2, QTableWidgetItem(sender["name"]))
            self.sender_table.setItem(row_position, 3, QTableWidgetItem(sender.get("address_detail", "")))
            self.sender_table.setItem(row_position, 4, QTableWidgetItem(sender.get("sub_district", "")))
            self.sender_table.setItem(row_position, 5, QTableWidgetItem(sender.get("district", "")))
            self.sender_table.setItem(row_position, 6, QTableWidgetItem(sender.get("province", "")))
            self.sender_table.setItem(row_position, 7, QTableWidgetItem(sender["post_code"]))
            self.sender_table.setItem(row_position, 8, QTableWidgetItem(sender["tel"]))
        
        self.populate_inventory_dropdown()
        if self.search_input:
            self.search_input.clear()

    def on_sender_selection_changed(self):
        if self.sender_table.selectedItems():
            self.show_edit_form()

    def show_add_form(self):
        self.sender_table.clearSelection()
        self.current_sender_id = None
        self.form_groupbox.setTitle("Add New Sender")
        self.delete_button.setVisible(False)
        self.name_input.clear()
        self.address_detail_input.clear()
        self.tel_input.clear()
        
        default_code = get_config("bills_process_inventory_code")
        if default_code:
            self.inventory_combo.setCurrentText(default_code)
        else:
            self.inventory_combo.setCurrentIndex(-1)

        self.initialize_address_dropdowns()
        self.postcode_input.clear()
        self.name_input.setFocus()

    def show_edit_form(self):
        selected_row = self.sender_table.currentRow()
        if selected_row < 0:
            return

        self.current_sender_id = int(self.sender_table.item(selected_row, 0).text())
        
        self.form_groupbox.setTitle("Edit Sender")
        self.inventory_combo.setCurrentText(self.sender_table.item(selected_row, 1).text())
        self.name_input.line_edit.setText(self.sender_table.item(selected_row, 2).text())
        
        address_detail = self.sender_table.item(selected_row, 3).text()
        sub_district = self.sender_table.item(selected_row, 4).text()
        district = self.sender_table.item(selected_row, 5).text()
        province = self.sender_table.item(selected_row, 6).text()
        post_code = self.sender_table.item(selected_row, 7).text()
        tel = self.sender_table.item(selected_row, 8).text()

        self.tel_input.line_edit.setText(tel)
        self.address_detail_input.line_edit.setText(address_detail)
        self.postcode_input.setText(post_code)

        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.sub_district_combo.blockSignals(True)

        self.initialize_address_dropdowns()
        self.province_combo.setCurrentText(province)

        self.district_combo.clear()
        if province:
            districts = get_districts(province)
            if districts:
                self.district_combo.addItems(districts)
                self.district_combo.setEnabled(True)
        self.district_combo.setCurrentText(district)

        self.sub_district_combo.clear()
        if province and district:
            sub_districts = get_sub_districts(province, district)
            if sub_districts:
                self.sub_district_combo.addItems(sub_districts)
                self.sub_district_combo.setEnabled(True)
        self.sub_district_combo.setCurrentText(sub_district)

        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.sub_district_combo.blockSignals(False)

        self.delete_button.setVisible(True)

    def delete_selected_sender(self):
        if self.current_sender_id is None:
            return

        reply = QMessageBox.question(self, 'Delete Sender',
                                     "Are you sure you want to delete this sender?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_sender(self.current_sender_id)
            if success:
                QMessageBox.information(self, "Success", "Sender deleted successfully.")
                self.load_senders_to_table()
                self.show_add_form()
            else:
                QMessageBox.warning(self, "Error", message)

    def save_sender(self):
        self.name_input._validate_input()
        self.address_detail_input._validate_input()
        self.tel_input._validate_input()

        inventory = self.inventory_combo.currentText()
        name = self.name_input.text()
        tel = self.tel_input.text()
        
        province = self.province_combo.currentText()
        district = self.district_combo.currentText()
        sub_district = self.sub_district_combo.currentText()
        address_detail = self.address_detail_input.text()
        post_code = self.postcode_input.text()

        is_address_filled = not any(s.startswith('Select') for s in [province, district, sub_district])

        if not all([
            self.name_input.isValid(),
            self.address_detail_input.isValid(),
            self.tel_input.isValid(),
            inventory,
            post_code,
            is_address_filled
        ]):
            self.name_input.show_error_if_invalid()
            self.address_detail_input.show_error_if_invalid()
            self.tel_input.show_error_if_invalid()
            QMessageBox.warning(self, "Input Error", "Please fill in all fields correctly and ensure they are valid.")
            return

        if self.current_sender_id is None:
            success, message = add_sender(
                inventory_code=inventory, name=name, address_detail=address_detail,
                sub_district=sub_district, district=district, province=province,
                post_code=post_code, tel=tel
            )
        else:
            success, message = update_sender(
                sender_id=self.current_sender_id, inventory_code=inventory, name=name,
                address_detail=address_detail, sub_district=sub_district, district=district,
                province=province, post_code=post_code, tel=tel
            )

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_senders_to_table()
            self.show_add_form()
        else:
            QMessageBox.warning(self, "Database Error", message)
