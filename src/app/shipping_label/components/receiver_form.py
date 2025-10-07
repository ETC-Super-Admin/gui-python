from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QComboBox, QMessageBox
)
from PySide6.QtCore import Signal
import qtawesome as qta

from src.db.address_queries import get_provinces, get_districts, get_sub_districts, get_zipcode, get_addresses_by_zipcode
from src.db.config_queries import get_config
from src.db.path_config_queries import get_all_path_configs
from src.db.delivery_by_queries import get_all_delivery_options
from src.components.validated_line_edit import ValidatedLineEdit

class ReceiverForm(QWidget):
    """
    A form widget for creating and editing receiver details.
    Handles UI, validation, and address lookup.
    """
    save_requested = Signal(dict)      # Emits receiver data
    delete_requested = Signal(int)      # Emits receiver ID
    cancel_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_receiver_id = None
        self.setup_ui()
        self.initialize_address_dropdowns()
        self.populate_delivery_dropdown()
        self.populate_inventory_dropdown()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.form_groupbox = QGroupBox("Manage Receiver")
        self.form_groupbox.setObjectName("Card")
        form_layout = QFormLayout(self.form_groupbox)
        form_layout.setSpacing(10)

        # --- Form Fields ---
        self.inventory_combo = QComboBox()
        form_layout.addRow("Inventory:", self.inventory_combo)

        self.name_input = self._create_validated_line_edit("Enter receiver's name", lambda text: (len(text.strip()) >= 3, "Name must be at least 3 characters."))
        form_layout.addRow("Name:", self.name_input)

        postcode_layout = self._create_postcode_lookup()
        form_layout.addRow("Post Code Lookup:", postcode_layout)

        self.province_combo = QComboBox()
        self.district_combo = QComboBox()
        self.sub_district_combo = QComboBox()
        form_layout.addRow("Province:", self.province_combo)
        form_layout.addRow("District:", self.district_combo)
        form_layout.addRow("Sub-district:", self.sub_district_combo)

        self.address_detail_input = self._create_validated_line_edit("House No., Street, etc.", lambda text: (text.strip() != "", "Address details cannot be empty."))
        form_layout.addRow("Address Details:", self.address_detail_input)

        self.tel_input = self._create_validated_line_edit("Enter tel. numbers, separated by commas", lambda text: (text.strip() != "", "Tel. cannot be empty."))
        form_layout.addRow("Tel.:", self.tel_input)

        self.delivery_by_combo = QComboBox()
        form_layout.addRow("Delivery By:", self.delivery_by_combo)

        # --- Action Buttons ---
        form_action_layout = self._create_action_buttons()
        form_layout.addRow(form_action_layout)

        layout.addWidget(self.form_groupbox)
        layout.addStretch()

        # --- Connect Signals ---
        self.province_combo.currentTextChanged.connect(self.on_province_changed)
        self.district_combo.currentTextChanged.connect(self.on_district_changed)
        self.sub_district_combo.currentTextChanged.connect(self.on_sub_district_changed)

    def _create_validated_line_edit(self, placeholder, validation_func):
        return ValidatedLineEdit(
            placeholder_text=placeholder,
            validation_func=validation_func,
            validation_mode='on_demand'
        )

    def _create_postcode_lookup(self):
        self.postcode_input = QLineEdit()
        self.postcode_input.setPlaceholderText("Enter 5-digit post code")
        self.postcode_input.returnPressed.connect(self.on_find_by_zipcode_clicked)
        find_zip_button = QPushButton(qta.icon('fa5s.search', color='white'), " Find")
        find_zip_button.clicked.connect(self.on_find_by_zipcode_clicked)
        postcode_layout = QHBoxLayout()
        postcode_layout.addWidget(self.postcode_input)
        postcode_layout.addWidget(find_zip_button)
        return postcode_layout

    def _create_action_buttons(self):
        form_action_layout = QHBoxLayout()
        self.cancel_button = QPushButton(qta.icon('fa5s.times', color='#64748b'), " Cancel")
        self.cancel_button.setObjectName("CancelFormButton")
        self.cancel_button.clicked.connect(self.cancel_requested.emit)

        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save")
        self.save_button.setObjectName("SaveUserButton")
        self.save_button.clicked.connect(self.save_receiver)
        
        self.delete_button = QPushButton(qta.icon('fa5s.trash-alt', color='white'), " Delete")
        self.delete_button.setObjectName("DeleteUserButton")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.current_receiver_id))
        self.delete_button.setVisible(False)

        form_action_layout.addStretch()
        form_action_layout.addWidget(self.cancel_button)
        form_action_layout.addWidget(self.delete_button)
        form_action_layout.addWidget(self.save_button)
        return form_action_layout

    # --- Data Population and Initialization ---
    def populate_inventory_dropdown(self):
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

    def populate_delivery_dropdown(self):
        self.delivery_by_combo.blockSignals(True)
        current_text = self.delivery_by_combo.currentText()
        self.delivery_by_combo.clear()
        options = get_all_delivery_options()
        if options:
            self.delivery_by_combo.addItems(options)
        if current_text in options:
            self.delivery_by_combo.setCurrentText(current_text)
        else:
            default_delivery = get_config("default_delivery_by")
            if default_delivery in options:
                self.delivery_by_combo.setCurrentText(default_delivery)
        self.delivery_by_combo.blockSignals(False)

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

    # --- Address Logic ---
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
        
        # Block signals to prevent cascading updates while we set the values
        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.sub_district_combo.blockSignals(True)

        province = results[0]['province']
        self.province_combo.setCurrentText(province)
        
        districts = sorted(list(set(row['district'] for row in results)))
        self.district_combo.clear(); self.district_combo.addItems(districts); self.district_combo.setEnabled(True)
        
        sub_districts = sorted(list(set(row['sub_district'] for row in results)))
        self.sub_district_combo.clear(); self.sub_district_combo.addItems(sub_districts); self.sub_district_combo.setEnabled(True)

        # Unblock signals
        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.sub_district_combo.blockSignals(False)

        if len(districts) == 1: self.district_combo.setCurrentText(districts[0])
        if len(sub_districts) == 1: self.sub_district_combo.setCurrentText(sub_districts[0])

    # --- Public Methods ---
    def set_add_mode(self):
        self.current_receiver_id = None
        self.form_groupbox.setTitle("Add New Receiver")
        self.delete_button.setVisible(False)
        self.name_input.clear()
        self.address_detail_input.clear()
        self.tel_input.clear()
        
        default_code = get_config("bills_process_inventory_code")
        self.inventory_combo.setCurrentText(default_code if default_code else "")
        
        default_delivery = get_config("default_delivery_by")
        self.delivery_by_combo.setCurrentText(default_delivery if default_delivery else "")

        self.initialize_address_dropdowns()
        self.postcode_input.clear()
        self.name_input.setFocus()
        self.show()

    def set_edit_mode(self, receiver_data):
        self.current_receiver_id = receiver_data["id"]
        self.form_groupbox.setTitle(f'Edit Receiver: {receiver_data["name"]}')

        # Block signals during population
        self.province_combo.blockSignals(True)
        self.district_combo.blockSignals(True)
        self.sub_district_combo.blockSignals(True)

        self.inventory_combo.setCurrentText(receiver_data.get("inventory_code", ""))
        self.name_input.line_edit.setText(receiver_data.get("name", ""))
        self.address_detail_input.line_edit.setText(receiver_data.get("address_detail", ""))
        self.tel_input.line_edit.setText(receiver_data.get("tel", ""))
        self.postcode_input.setText(receiver_data.get("post_code", ""))
        self.delivery_by_combo.setCurrentText(receiver_data.get("delivery_by", ""))

        # Set address dropdowns
        province = receiver_data.get("province", "")
        self.initialize_address_dropdowns()
        self.province_combo.setCurrentText(province)
        
        district = receiver_data.get("district", "")
        if province:
            districts = get_districts(province)
            if districts:
                self.district_combo.addItems(districts)
                self.district_combo.setEnabled(True)
        self.district_combo.setCurrentText(district)

        sub_district = receiver_data.get("sub_district", "")
        if province and district:
            sub_districts = get_sub_districts(province, district)
            if sub_districts:
                self.sub_district_combo.addItems(sub_districts)
                self.sub_district_combo.setEnabled(True)
        self.sub_district_combo.setCurrentText(sub_district)

        # Unblock signals
        self.province_combo.blockSignals(False)
        self.district_combo.blockSignals(False)
        self.sub_district_combo.blockSignals(False)

        self.delete_button.setVisible(True)
        self.show()

    def save_receiver(self):
        # Trigger validation on all fields
        self.name_input._validate_input()
        self.address_detail_input._validate_input()
        self.tel_input._validate_input()

        # Collect data
        data = {
            "id": self.current_receiver_id,
            "inventory_code": self.inventory_combo.currentText(),
            "name": self.name_input.text(),
            "tel": self.tel_input.text(),
            "province": self.province_combo.currentText(),
            "district": self.district_combo.currentText(),
            "sub_district": self.sub_district_combo.currentText(),
            "address_detail": self.address_detail_input.text(),
            "post_code": self.postcode_input.text(),
            "delivery_by": self.delivery_by_combo.currentText()
        }

        # Validate data
        is_address_filled = not any(s.startswith('Select') for s in [data["province"], data["district"], data["sub_district"]])
        if not all([
            self.name_input.isValid(), self.address_detail_input.isValid(), self.tel_input.isValid(),
            data["inventory_code"], data["post_code"], is_address_filled, data["delivery_by"]
        ]):
            self.name_input.show_error_if_invalid()
            self.address_detail_input.show_error_if_invalid()
            self.tel_input.show_error_if_invalid()
            QMessageBox.warning(self, "Input Error", "Please fill in all fields correctly and ensure they are valid.")
            return

        self.save_requested.emit(data)
