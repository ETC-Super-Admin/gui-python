from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QComboBox, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
import qtawesome as qta

# Database imports
from src.db.sender_queries import initialize_sender_db, add_sender, get_all_senders, update_sender, delete_sender
from src.db.address_queries import get_provinces, get_districts, get_sub_districts, get_zipcode, get_addresses_by_zipcode

class SenderManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_sender_id = None
        initialize_sender_db()
        self.setup_ui()
        self.load_senders_to_table()
        self.initialize_address_dropdowns()
        self.show_add_form()

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
        table_title = QLabel("All Senders")
        table_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()

        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Sender")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.show_add_form)
        table_header_layout.addWidget(self.add_button)
        
        left_layout.addLayout(table_header_layout)

        self.sender_table = QTableWidget()
        self.sender_table.setObjectName("Card")
        self.sender_table.setColumnCount(6)
        self.sender_table.setHorizontalHeaderLabels(["ID", "Inventory", "Name", "Address", "Post Code", "Tel."])
        self.sender_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sender_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sender_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.sender_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sender_table.setColumnHidden(0, True)
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
        self.inventory_combo.addItems(["BKK", "PHK"])
        form_layout.addRow("Inventory:", self.inventory_combo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter sender's name")
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

        self.address_detail_input = QLineEdit()
        self.address_detail_input.setPlaceholderText("House No., Street, etc.")
        form_layout.addRow("Address Details:", self.address_detail_input)
        # --- End New Address Fields ---

        self.tel_input = QLineEdit()
        self.tel_input.setPlaceholderText("Enter tel. numbers, separated by commas")
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

        # Block signals to prevent cascading updates
        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.sub_district_combo.blockSignals(True)

        # A single postcode almost always belongs to a single province.
        province = results[0]['province']
        self.province_combo.setCurrentText(province)

        # Repopulate districts for the found province
        districts = sorted(list(set(row['district'] for row in results)))
        self.district_combo.clear()
        self.district_combo.addItems(districts)
        self.district_combo.setEnabled(True)

        # Repopulate sub-districts for the found province and first district
        sub_districts = sorted(list(set(row['sub_district'] for row in results)))
        self.sub_district_combo.clear()
        self.sub_district_combo.addItems(sub_districts)
        self.sub_district_combo.setEnabled(True)

        # Unblock signals
        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.sub_district_combo.blockSignals(False)

        # If only one result, select it all
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
            self.sender_table.setItem(row_position, 3, QTableWidgetItem(sender["address"])) 
            self.sender_table.setItem(row_position, 4, QTableWidgetItem(sender["post_code"]))
            self.sender_table.setItem(row_position, 5, QTableWidgetItem(sender["tel"]))

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
        self.inventory_combo.setCurrentIndex(0)
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
        self.name_input.setText(self.sender_table.item(selected_row, 2).text())
        self.tel_input.setText(self.sender_table.item(selected_row, 5).text())
        
        self.initialize_address_dropdowns()
        self.address_detail_input.setText(self.sender_table.item(selected_row, 3).text())
        self.postcode_input.setText(self.sender_table.item(selected_row, 4).text())
        
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
        inventory = self.inventory_combo.currentText()
        name = self.name_input.text()
        tel = self.tel_input.text()
        
        province = self.province_combo.currentText()
        district = self.district_combo.currentText()
        sub_district = self.sub_district_combo.currentText()
        address_detail = self.address_detail_input.text()
        post_code = self.postcode_input.text()

        is_address_filled = not any(s.startswith('Select') for s in [province, district, sub_district])

        if not all([inventory, name, tel, address_detail, post_code, is_address_filled]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields, including a full address.")
            return

        full_address = f"{address_detail}, {sub_district}, {district}, {province}"

        if self.current_sender_id is None:
            success, message = add_sender(inventory, name, full_address, post_code, tel)
        else:
            success, message = update_sender(self.current_sender_id, inventory, name, full_address, post_code, tel)

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_senders_to_table()
            self.show_add_form()
        else:
            QMessageBox.warning(self, "Database Error", message)