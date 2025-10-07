from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QGroupBox,
    QDialog, QDialogButtonBox, QLineEdit, QFormLayout, QFileDialog
)
from PySide6.QtCore import Qt, QSettings, QStandardPaths
import qtawesome as qta
import openpyxl
from datetime import datetime
import os

# Utility Imports
from src.utils.excel_importer import read_excel_to_dict_list

# Refactored Component Imports
from .components.receiver_table_view import ReceiverTableView
from .components.receiver_form import ReceiverForm

# Database Imports
from src.db.receiver_queries import (
    initialize_receiver_db, get_all_receiver_identities, get_addresses_for_receiver,
    add_receiver_identity, add_receiver_address, update_receiver_identity, 
    update_receiver_address, delete_receiver_identity, delete_receiver_address,
    get_receiver_address_by_id, find_exact_address, get_all_receiver_addresses
)
from src.db.delivery_by_queries import initialize_delivery_db, get_all_delivery_options, add_delivery_option

class ReceiverIdentityDialog(QDialog):
    """Dialog for adding or editing a receiver's name and telephone."""
    def __init__(self, current_name="", current_tel="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Receiver Details")
        
        layout = QFormLayout(self)
        self.name_input = QLineEdit(current_name)
        self.tel_input = QLineEdit(current_tel)
        layout.addRow("Name:", self.name_input)
        layout.addRow("Telephone:", self.tel_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_data(self):
        return self.name_input.text().strip(), self.tel_input.text().strip()

class ReceiverManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_receiver_id = None
        self.current_address_id = None

        initialize_receiver_db()
        initialize_delivery_db()
        
        self.setup_ui()
        self.connect_signals()
        self.load_receivers_to_table()
        self.address_details_group.hide()
        self.address_form_widget.hide()

    def showEvent(self, event):
        super().showEvent(event)
        if self.isVisible():
            self.load_receivers_to_table()
            self.address_form_widget.populate_delivery_dropdown()
            self.address_form_widget.populate_inventory_dropdown()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_layout = QHBoxLayout()
        title_label = QLabel("Receiver Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.import_button = QPushButton(qta.icon('fa5s.file-import', color='white'), " Import Excel")
        self.import_button.setObjectName("EditUserButton")
        self.export_button = QPushButton(qta.icon('fa5s.file-export', color='white'), " Export Excel")
        self.export_button.setObjectName("ExportButton")
        
        title_layout.addWidget(self.import_button)
        title_layout.addWidget(self.export_button)
        main_layout.addLayout(title_layout)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- Left Side (Master Receiver List) ---
        self.receivers_table_widget = ReceiverTableView()
        content_layout.addWidget(self.receivers_table_widget, 3)

        # --- Right Side (Address Details) ---
        right_side_widget = QWidget()
        right_layout = QVBoxLayout(right_side_widget)
        right_layout.setContentsMargins(0,0,0,0)
        content_layout.addWidget(right_side_widget, 7)

        self.address_details_group = QGroupBox("Addresses")
        self.address_details_group.setObjectName("Card")
        details_layout = QVBoxLayout(self.address_details_group)
        right_layout.addWidget(self.address_details_group)

        address_actions_layout = QHBoxLayout()
        self.receiver_name_label = QLabel("")
        self.receiver_name_label.setStyleSheet("font-weight: bold;")
        address_actions_layout.addWidget(self.receiver_name_label)
        address_actions_layout.addStretch()
        
        self.edit_receiver_button = QPushButton(qta.icon('fa5s.edit', color='#64748b'), " Edit Receiver")
        self.delete_receiver_button = QPushButton(qta.icon('fa5s.trash-alt', color='#ef4444'), " Delete Receiver")
        self.add_address_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Address")
        self.add_address_button.setObjectName("AddUserButton")

        address_actions_layout.addWidget(self.edit_receiver_button)
        address_actions_layout.addWidget(self.delete_receiver_button)
        address_actions_layout.addWidget(self.add_address_button)
        details_layout.addLayout(address_actions_layout)

        self.address_table = self._create_address_table()
        details_layout.addWidget(self.address_table)

        self.address_form_widget = ReceiverForm()
        right_layout.addWidget(self.address_form_widget)

    def _create_address_table(self):
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(["ID", "Inventory", "Address", "Sub-district", "District", "Province", "Post Code", "Delivery By", "Zone"])
        table.setColumnHidden(0, True)
        header = table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return table

    def connect_signals(self):
        self.receivers_table_widget.receiver_selected.connect(self.on_receiver_selected)
        self.receivers_table_widget.add_receiver_requested.connect(self.add_new_receiver)

        self.import_button.clicked.connect(self.import_from_excel)
        self.export_button.clicked.connect(self.export_all_receivers_data)

        self.edit_receiver_button.clicked.connect(self.edit_receiver)
        self.delete_receiver_button.clicked.connect(self.delete_receiver)
        self.add_address_button.clicked.connect(self.add_address)
        self.address_table.itemSelectionChanged.connect(self.on_address_selected)

        self.address_form_widget.save_requested.connect(self.save_address_form)
        self.address_form_widget.delete_requested.connect(self.delete_address)
        self.address_form_widget.cancel_requested.connect(lambda: self.address_form_widget.hide())

    def load_receivers_to_table(self):
        receivers = get_all_receiver_identities()
        self.receivers_table_widget.populate_table(receivers)

    def on_receiver_selected(self, receiver_id):
        self.address_form_widget.hide()
        self.current_receiver_id = receiver_id
        self.address_table.clearSelection()

        if receiver_id > 0:
            self.address_details_group.show()
            receiver_name = self.receivers_table_widget.table.item(self.receivers_table_widget.table.currentRow(), 1).text()
            self.receiver_name_label.setText(f"Showing addresses for: {receiver_name}")
            self.populate_address_table(receiver_id)
        else:
            self.address_details_group.hide()
            self.receiver_name_label.setText("")
            self.populate_address_table(-1)

    def populate_address_table(self, receiver_id):
        self.address_table.setRowCount(0)
        if receiver_id < 0: return

        addresses = get_addresses_for_receiver(receiver_id)
        for addr in addresses:
            row = self.address_table.rowCount()
            self.address_table.insertRow(row)
            self.address_table.setItem(row, 0, QTableWidgetItem(str(addr["id"])))
            self.address_table.setItem(row, 1, QTableWidgetItem(addr["inventory_code"]))
            self.address_table.setItem(row, 2, QTableWidgetItem(addr["address_detail"]))
            self.address_table.setItem(row, 3, QTableWidgetItem(addr["sub_district"]))
            self.address_table.setItem(row, 4, QTableWidgetItem(addr["district"]))
            self.address_table.setItem(row, 5, QTableWidgetItem(addr["province"]))
            self.address_table.setItem(row, 6, QTableWidgetItem(addr["post_code"]))
            self.address_table.setItem(row, 7, QTableWidgetItem(addr["delivery_by"]))
            self.address_table.setItem(row, 8, QTableWidgetItem(addr.get("zone", "")))

    def on_address_selected(self):
        selected = self.address_table.selectedItems()
        if not selected: 
            self.current_address_id = None
            return
        
        self.current_address_id = int(self.address_table.item(selected[0].row(), 0).text())
        address_data = get_receiver_address_by_id(self.current_address_id)
        if address_data:
            self.address_form_widget.set_edit_mode(address_data)
            self.address_form_widget.show()

    def add_new_receiver(self):
        dialog = ReceiverIdentityDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            name, tel = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Input Error", "Receiver name cannot be empty.")
                return
            
            receiver_id, msg = add_receiver_identity(name, tel)
            if receiver_id is not None:
                self.load_receivers_to_table()
                self.receivers_table_widget.select_row_by_id(receiver_id)
                QMessageBox.information(self, "Receiver Added", f"{msg} Now, please add their first address.")
                self.add_address()
            else:
                QMessageBox.warning(self, "Error", msg)

    def edit_receiver(self):
        if not self.current_receiver_id: return
        
        current_row = self.receivers_table_widget.table.currentRow()
        name = self.receivers_table_widget.table.item(current_row, 1).text()
        tel = self.receivers_table_widget.table.item(current_row, 2).text()

        dialog = ReceiverIdentityDialog(name, tel, self)
        if dialog.exec() == QDialog.Accepted:
            new_name, new_tel = dialog.get_data()
            if not new_name:
                QMessageBox.warning(self, "Input Error", "Receiver name cannot be empty.")
                return
            success, msg = update_receiver_identity(self.current_receiver_id, new_name, new_tel)
            if success:
                self.load_receivers_to_table()
                self.receivers_table_widget.select_row_by_id(self.current_receiver_id)
            else:
                QMessageBox.warning(self, "Error", msg)

    def delete_receiver(self):
        if not self.current_receiver_id: return
        reply = QMessageBox.question(self, 'Delete Receiver', "Are you sure you want to delete this receiver and ALL their addresses?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = delete_receiver_identity(self.current_receiver_id)
            if success:
                self.load_receivers_to_table()
            else:
                QMessageBox.warning(self, "Error", msg)

    def add_address(self):
        if not self.current_receiver_id: return
        self.address_table.clearSelection()
        self.address_form_widget.set_add_mode()
        self.address_form_widget.show()

    def delete_address(self, address_id):
        if not address_id: return
        reply = QMessageBox.question(self, 'Delete Address', "Are you sure you want to delete this address?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = delete_receiver_address(address_id)
            if success:
                self.populate_address_table(self.current_receiver_id)
                self.address_form_widget.hide()
            else:
                QMessageBox.warning(self, "Error", msg)

    def save_address_form(self, data):
        if self.current_address_id and data.get('id') == self.current_address_id: # Update
            success, msg = update_receiver_address(self.current_address_id, data)
        else: # Add
            success, msg = add_receiver_address(self.current_receiver_id, data)

        if success:
            self.populate_address_table(self.current_receiver_id)
            self.address_form_widget.hide()
        else:
            QMessageBox.warning(self, "Database Error", msg)

    def export_all_receivers_data(self):
        self.export_button.setText("Exporting...")
        self.export_button.setEnabled(False)
        try:
            all_data = get_all_receiver_addresses()
            if not all_data:
                QMessageBox.information(self, "Export", "There is no receiver data to export.")
                return

            headers = ["Name", "Tel", "Inventory", "Address Details", "Sub-district", "District", "Province", "Post Code", "Delivery By", "Zone"]
            key_map = {
                "Name": "name",
                "Tel": "tel",
                "Inventory": "inventory_code",
                "Address Details": "address_detail",
                "Sub-district": "sub_district",
                "District": "district",
                "Province": "province",
                "Post Code": "post_code",
                "Delivery By": "delivery_by",
                "Zone": "zone"
            }
            
            settings = QSettings("ProAuto", "App")
            last_dir = settings.value("excel/last_export_directory", QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"receivers_export_{timestamp}.xlsx"
            
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", os.path.join(last_dir, default_filename), "Excel Files (*.xlsx)")

            if not file_path: return

            settings.setValue("excel/last_export_directory", os.path.dirname(file_path))

            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Receivers"
            sheet.append(headers)

            for row_data in all_data:
                sheet.append([row_data.get(key_map[h], "") for h in headers])

            for col_idx, header in enumerate(headers, 1):
                column_letter = openpyxl.utils.get_column_letter(col_idx)
                max_length = len(header)
                for row_data in all_data:
                    cell_value = str(row_data.get(key_map[header], ""))
                    if len(cell_value) > max_length:
                        max_length = len(cell_value)
                sheet.column_dimensions[column_letter].width = (max_length + 2) * 1.2

            workbook.save(file_path)
            QMessageBox.information(self, "Export Successful", f"Data exported to\n{file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"An error occurred: {e}")
        finally:
            self.export_button.setText("Export Excel")
            self.export_button.setEnabled(True)

    def import_from_excel(self):
        self.import_button.setText("Importing...")
        self.import_button.setEnabled(False)
        try:
            imported_data, filename = read_excel_to_dict_list(self)
            if not imported_data: return

            added_count, updated_count, unchanged_count = 0, 0, 0
            delivery_options = set(get_all_delivery_options())

            for row_data in imported_data:
                name = row_data.get('Name')
                tel = str(row_data.get('Tel', ''))
                if not name: continue

                receiver_id, _ = add_receiver_identity(name, tel)
                if receiver_id is None: continue

                delivery_by = row_data.get('Delivery By', '').strip()
                if delivery_by and delivery_by not in delivery_options:
                    add_delivery_option(delivery_by)
                    delivery_options.add(delivery_by)

                address_data = {
                    'inventory_code': row_data.get('Inventory', ''),
                    'address_detail': row_data.get('Address Details', ''),
                    'sub_district': row_data.get('Sub-district', ''),
                    'district': row_data.get('District', ''),
                    'province': row_data.get('Province', ''),
                    'post_code': str(row_data.get('Post Code', '')),
                    'delivery_by': delivery_by,
                    'zone': str(row_data.get('Zone', ''))
                }

                existing_address = find_exact_address(receiver_id, address_data['address_detail'], address_data['post_code'])

                if existing_address:
                    is_different = any(str(existing_address.get(k, '')) != str(v) for k, v in address_data.items())
                    if is_different:
                        update_receiver_address(existing_address['id'], address_data)
                        updated_count += 1
                    else:
                        unchanged_count += 1
                else:
                    add_receiver_address(receiver_id, address_data)
                    added_count += 1

            self.load_receivers_to_table()
            QMessageBox.information(self, "Import Complete", 
                                    f"Successfully imported from {filename}\n\n"
                                    f"New addresses added: {added_count}\n"
                                    f"Addresses updated: {updated_count}\n"
                                    f"Unchanged items: {unchanged_count}")
        finally:
            self.import_button.setText("Import Excel")
            self.import_button.setEnabled(True)
