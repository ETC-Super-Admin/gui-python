from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtGui import QKeySequence, QShortcut

# Utility Imports
from src.utils.excel_exporter import export_table_to_excel

# Refactored Component Imports
from .components.receiver_table_view import ReceiverTableView
from .components.receiver_form import ReceiverForm

# Database Imports
from src.db.receiver_queries import (
    initialize_receiver_db, add_receiver, get_all_receivers, update_receiver, delete_receiver, get_receiver_by_id
)
from src.db.delivery_by_queries import initialize_delivery_db

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

        # Left Side (Table)
        self.table_widget = ReceiverTableView()
        content_layout.addWidget(self.table_widget, 7)

        # Right Side (Form)
        self.form_widget = ReceiverForm()
        content_layout.addWidget(self.form_widget, 3)

        # --- Add Keyboard Shortcut for Saving ---
        shortcut = QShortcut(QKeySequence("Shift+Return"), self)
        shortcut.activated.connect(self.form_widget.save_receiver)

    def connect_signals(self):
        # Table signals
        self.table_widget.add_receiver_requested.connect(self.show_add_form)
        self.table_widget.edit_receiver_requested.connect(self.show_edit_form)
        self.table_widget.import_requested.connect(self.import_from_excel)
        self.table_widget.export_requested.connect(self.export_to_excel)

        # Form signals
        self.form_widget.save_requested.connect(self.save_receiver)
        self.form_widget.delete_requested.connect(self.delete_receiver)
        self.form_widget.cancel_requested.connect(self.show_table_only_view)

    def load_receivers_to_table(self):
        receivers = get_all_receivers()
        self.table_widget.populate_table(receivers)

    # --- View Management --- 
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

    # --- Data Operations ---
    def save_receiver(self, data):
        if data['id'] is None: # Add new
            success, message = add_receiver(
                inventory_code=data['inventory_code'], name=data['name'], address_detail=data['address_detail'],
                sub_district=data['sub_district'], district=data['district'], province=data['province'],
                post_code=data['post_code'], tel=data['tel'], delivery_by=data['delivery_by'], zone=data['zone']
            )
        else: # Update existing
            success, message = update_receiver(
                receiver_id=data['id'], inventory_code=data['inventory_code'], name=data['name'],
                address_detail=data['address_detail'], sub_district=data['sub_district'], district=data['district'],
                province=data['province'], post_code=data['post_code'], tel=data['tel'], delivery_by=data['delivery_by'], zone=data['zone']
            )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_receivers_to_table()
            self.show_table_only_view()
        else:
            QMessageBox.warning(self, "Database Error", message)

    def delete_receiver(self, receiver_id):
        reply = QMessageBox.question(self, 'Delete Receiver',
                                     "Are you sure you want to delete this receiver?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = delete_receiver(receiver_id)
            if success:
                QMessageBox.information(self, "Success", "Receiver deleted successfully.")
                self.load_receivers_to_table()
                self.show_table_only_view()
            else:
                QMessageBox.warning(self, "Error", message)

    def import_from_excel(self):
        QMessageBox.information(self, "Import from Excel", "This feature is not yet implemented.")

    def export_to_excel(self):
        export_table_to_excel(self, self.table_widget.table, "Receivers", button=self.table_widget.export_button)
