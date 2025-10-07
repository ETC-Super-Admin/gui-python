from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtGui import QKeySequence, QShortcut

# Utility Imports
from src.utils.excel_exporter import export_table_to_excel
from src.utils.excel_importer import read_excel_to_dict_list

# Refactored Component Imports
from .components.receiver_table_view import ReceiverTableView
from .components.receiver_form import ReceiverForm

# Database Imports
from src.db.receiver_queries import (
    initialize_receiver_db, add_receiver, get_all_receivers, update_receiver, 
    delete_receiver, get_receiver_by_id, get_all_receivers_as_dict
)
from src.db.delivery_by_queries import initialize_delivery_db, get_all_delivery_options, add_delivery_option

class ReceiverManagement(QWidget):
    def __init__(self):
        super().__init__()
        initialize_receiver_db()
        initialize_delivery_db()
        self.setup_ui()
        self.connect_signals()
        self.load_receivers_to_table()
        self.show_table_only_view() # Hide form by default

    def showEvent(self, event):
        """Override showEvent to refresh data when the widget is shown."""
        super().showEvent(event)
        if self.isVisible():
            self.load_receivers_to_table()
            self.form_widget.populate_delivery_dropdown()
            self.form_widget.populate_inventory_dropdown()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("Receiver Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.table_widget = ReceiverTableView()
        content_layout.addWidget(self.table_widget, 7)

        self.form_widget = ReceiverForm()
        content_layout.addWidget(self.form_widget, 3)

        shortcut = QShortcut(QKeySequence("Shift+Return"), self)
        shortcut.activated.connect(self.form_widget.save_receiver)

    def connect_signals(self):
        self.table_widget.add_receiver_requested.connect(self.show_add_form)
        self.table_widget.edit_receiver_requested.connect(self.show_edit_form)
        self.table_widget.import_requested.connect(self.import_from_excel)
        self.table_widget.export_requested.connect(self.export_to_excel)

        self.form_widget.save_requested.connect(self.save_receiver)
        self.form_widget.delete_requested.connect(self.delete_receiver)
        self.form_widget.cancel_requested.connect(self.show_table_only_view)

    def load_receivers_to_table(self):
        receivers = get_all_receivers()
        self.table_widget.populate_table(receivers)

    def show_table_only_view(self):
        self.form_widget.hide()
        self.table_widget.clear_selection()

    def show_add_form(self):
        self.table_widget.clear_selection()
        self.form_widget.set_add_mode()

    def show_edit_form(self, receiver_id):
        receiver_data = get_receiver_by_id(receiver_id)
        if receiver_data:
            self.form_widget.set_edit_mode(receiver_data)
        else:
            QMessageBox.warning(self, "Error", "Could not find receiver data.")
            self.show_table_only_view()

    def save_receiver(self, data):
        # This could also be a point of synchronization for delivery_by
        delivery_by = data.get('delivery_by')
        if delivery_by:
            existing_options = get_all_delivery_options()
            if delivery_by not in existing_options:
                add_delivery_option(delivery_by)
                self.form_widget.populate_delivery_dropdown()

        if data.get('id') is None:
            # Remove id from data dict if it's None before calling add_receiver
            data.pop('id', None) 
            success, message = add_receiver(**data)
        else:
            # Separate receiver_id for the update function signature
            receiver_id = data.pop('id', None)
            success, message = update_receiver(receiver_id=receiver_id, **data)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_receivers_to_table()
            self.show_table_only_view()
        else:
            QMessageBox.warning(self, "Database Error", message)

    def delete_receiver(self, receiver_id):
        reply = QMessageBox.question(self, 'Delete Receiver', "Are you sure?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_receiver(receiver_id)
            if success:
                QMessageBox.information(self, "Success", "Receiver deleted.")
                self.load_receivers_to_table()
                self.show_table_only_view()
            else:
                QMessageBox.warning(self, "Error", message)

    def export_to_excel(self):
        export_table_to_excel(self, self.table_widget.table, "Receivers", button=self.table_widget.export_button)

    def import_from_excel(self):
        button = self.table_widget.import_button
        original_text = button.text()
        button.setText("Importing...")
        button.setEnabled(False)

        try:
            imported_data, filename = read_excel_to_dict_list(self)
            if not imported_data:
                return

            db_receivers = get_all_receivers_as_dict()
            delivery_options = set(get_all_delivery_options())
            added_count, updated_count, unchanged_count = 0, 0, 0

            for row_data in imported_data:
                name = row_data.get('Name')
                if not name:
                    continue

                delivery_by = row_data.get('Delivery By', '').strip()
                if delivery_by and delivery_by not in delivery_options:
                    add_delivery_option(delivery_by)
                    delivery_options.add(delivery_by)

                mapped_data = {
                    'inventory_code': row_data.get('Inventory', ''), 'name': name,
                    'address_detail': row_data.get('Address Details', ''), 'sub_district': row_data.get('Sub-district', ''),
                    'district': row_data.get('District', ''), 'province': row_data.get('Province', ''),
                    'post_code': str(row_data.get('Post Code', '')), 'tel': str(row_data.get('Tel.', '')),
                    'delivery_by': delivery_by, 'zone': str(row_data.get('Zone', ''))
                }

                existing_receiver = db_receivers.get(name)
                if existing_receiver:
                    is_different = any(str(existing_receiver.get(k, '')) != str(v) for k, v in mapped_data.items())
                    if is_different:
                        update_receiver(receiver_id=existing_receiver['id'], **mapped_data)
                        updated_count += 1
                    else:
                        unchanged_count += 1
                else:
                    add_receiver(**mapped_data)
                    added_count += 1

            self.load_receivers_to_table()
            self.form_widget.populate_delivery_dropdown() # Refresh dropdown
            QMessageBox.information(self, "Import Complete", 
                                    f"Successfully imported from {filename}\n\n"
                                    f"New receivers added: {added_count}\n"
                                    f"Receivers updated: {updated_count}\n"
                                    f"Unchanged receivers: {unchanged_count}")

        finally:
            button.setText(original_text)
            button.setEnabled(True)
