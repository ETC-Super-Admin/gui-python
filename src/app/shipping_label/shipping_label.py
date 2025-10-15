from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QFrame, QGroupBox,
    QFormLayout, QComboBox, QLineEdit, QPushButton, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter

# Import components and DB queries
from src.components.custom_spinbox import CustomSpinBox
from src.components.flow_layout import FlowLayout
from src.app.shipping_label.components.receiver_table_view import ReceiverTableView
from src.app.shipping_label.components.label_preview import LabelPreview
from src.db.receiver_queries import get_all_receiver_identities, get_addresses_for_receiver, get_receiver_identity_by_id
from src.db.sender_queries import get_all_senders
from src.db.config_queries import get_config
from src.utils.widget_to_pdf import save_widget_as_pdf
from src.utils.direct_printer import page_setup, direct_print
import qtawesome as qta

class ShippingLabel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.senders_data = [] # Cache for sender data
        self.printer = QPrinter(QPrinter.HighResolution)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # --- Left Side (Live View) ---
        self.label_preview = LabelPreview()
        left_container = self._create_live_view_panel()

        # --- Right Side (Management with Splitter) ---
        right_splitter = QSplitter(Qt.Horizontal)
        right_splitter.setHandleWidth(12)

        # --- Right-Left Panel (Receiver List) ---
        management_panel_1 = QFrame()
        management_panel_1.setObjectName("Card")
        panel_1_layout = QVBoxLayout(management_panel_1)
        panel_1_layout.setContentsMargins(0, 0, 0, 0) # The card style provides padding
        self.receiver_list_view = ReceiverTableView(show_add_button=False)
        panel_1_layout.addWidget(self.receiver_list_view)

        management_panel_2 = self._create_management_panel_2()

        # Set a minimum width for both panels to ensure they resize gracefully
        management_panel_1.setMinimumWidth(300)
        management_panel_2.setMinimumWidth(300)

        right_splitter.addWidget(management_panel_1)
        right_splitter.addWidget(management_panel_2)
        
        # Set stretch factors for a 1:1 ratio
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(left_container, 1)
        main_layout.addWidget(right_splitter, 1)

        # Connect signals and load initial data
        self.receiver_list_view.receiver_selected.connect(self.on_receiver_selected)
        self.sender_combo.currentIndexChanged.connect(self.on_sender_selected)
        self.copies_spinbox.valueChanged.connect(self.on_copies_changed)

        # Connect text changed signals for live preview update
        self.sender_name_input.textChanged.connect(self._update_preview_from_inputs)
        self.sender_tel_input.textChanged.connect(self._update_preview_from_inputs)
        self.sender_address_input.textChanged.connect(self._update_preview_from_inputs)
        self.receiver_name_input.textChanged.connect(self._update_preview_from_inputs)
        self.receiver_tel_input.textChanged.connect(self._update_preview_from_inputs)
        self.receiver_address_input.textChanged.connect(self._update_preview_from_inputs)
        self.receiver_delivery_by_input.textChanged.connect(self._update_preview_from_inputs)
        self.receiver_note_input.textChanged.connect(self._update_preview_from_inputs)

        self.load_receiver_data()
        self.load_sender_data()

    def _update_preview_from_inputs(self):
        # Update sender info
        self.label_preview.update_sender_info(
            self.sender_address_input.text(),
            self.sender_tel_input.text()
        )
        # Update receiver info
        self.label_preview.update_receiver_info(
            self.receiver_name_input.text(),
            self.receiver_address_input.text(),
            self.receiver_tel_input.text(),
            self.receiver_delivery_by_input.text(),
            self.receiver_note_input.text()
        )

    def _create_live_view_panel(self):
        # Main container that centers the label
        container = QFrame()
        container.setObjectName("Card")
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.label_preview)
        return container

    def _create_management_panel_2(self):
        container = QFrame()
        container.setObjectName("Card")
        main_v_layout = QVBoxLayout(container)
        main_v_layout.setContentsMargins(8, 8, 8, 8)
        main_v_layout.setSpacing(15)

        # --- FROM Section ---
        from_group = QGroupBox("From")
        from_group.setObjectName("Card")
        from_layout = QVBoxLayout(from_group)
        from_layout.setSpacing(5)

        self.sender_combo = QComboBox()
        self.sender_name_input = QLineEdit()
        self.sender_tel_input = QLineEdit()
        self.sender_address_input = QLineEdit()
        
        from_layout.addWidget(QLabel("Sender:"))
        from_layout.addWidget(self.sender_combo)
        from_layout.addWidget(QLabel("Name:"))
        from_layout.addWidget(self.sender_name_input)
        from_layout.addWidget(QLabel("Tel:"))
        from_layout.addWidget(self.sender_tel_input)
        from_layout.addWidget(QLabel("Address:"))
        from_layout.addWidget(self.sender_address_input)
        from_layout.addStretch()
        main_v_layout.addWidget(from_group)

        # --- TO Section ---
        to_group = QGroupBox("To")
        to_group.setObjectName("Card")
        to_layout = QVBoxLayout(to_group)
        to_layout.setSpacing(5)

        self.receiver_name_input = QLineEdit()
        self.receiver_tel_input = QLineEdit()
        self.receiver_address_input = QLineEdit()
        self.receiver_delivery_by_input = QLineEdit()

        to_layout.addWidget(QLabel("Name:"))
        to_layout.addWidget(self.receiver_name_input)
        to_layout.addWidget(QLabel("Tel:"))
        to_layout.addWidget(self.receiver_tel_input)
        to_layout.addWidget(QLabel("Address:"))
        to_layout.addWidget(self.receiver_address_input)
        to_layout.addWidget(QLabel("Delivery by:"))
        to_layout.addWidget(self.receiver_delivery_by_input)

        self.receiver_note_input = QLineEdit()
        to_layout.addWidget(QLabel("Note:"))
        to_layout.addWidget(self.receiver_note_input)
        to_layout.addStretch()
        main_v_layout.addWidget(to_group)

        # --- PRINT Section ---
        print_group = QGroupBox("Print Options")
        print_group.setObjectName("Card")
        main_print_layout = QVBoxLayout(print_group)
        main_print_layout.setSpacing(10)

        # Top row for copies
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(QLabel("Copies:"))
        self.copies_spinbox = CustomSpinBox()
        self.copies_spinbox.setMinimum(1)
        self.copies_spinbox.setValue(1)
        top_row_layout.addWidget(self.copies_spinbox, 1)

        # Bottom row for main print actions using FlowLayout
        button_container = QWidget()
        bottom_row_layout = FlowLayout(button_container, spacing=10)
        bottom_row_layout.setAlignment(Qt.AlignRight) # Align buttons to the right

        page_setup_btn = QPushButton(qta.icon('fa5s.file', color='#64748b'), " Page Setup")
        page_setup_btn.setObjectName("PageSetupButton")
        page_setup_btn.clicked.connect(self.handle_page_setup)
        save_pdf_btn = QPushButton(qta.icon('fa5s.file-pdf', color='white'), " Save as PDF")
        save_pdf_btn.setObjectName("SavePdfButton")
        save_pdf_btn.clicked.connect(self.save_label_as_pdf)
        print_btn = QPushButton(qta.icon('fa5s.print', color='white'), " Print")
        print_btn.setObjectName("PrintButton")
        print_btn.clicked.connect(self.handle_direct_print)
        
        bottom_row_layout.addWidget(page_setup_btn)
        bottom_row_layout.addWidget(save_pdf_btn)
        bottom_row_layout.addWidget(print_btn)

        # Add rows to the main print layout
        main_print_layout.addLayout(top_row_layout)
        main_print_layout.addWidget(button_container)

        main_v_layout.addWidget(print_group)

        main_v_layout.addStretch()
        return container

    def handle_page_setup(self):
        page_setup(self, self.printer)

    def handle_direct_print(self):
        direct_print(self, self.label_preview, self.printer, self.copies_spinbox.value())

    def save_label_as_pdf(self):
        if not self.receiver_name_input.text():
            QMessageBox.warning(self, "Missing Data", "Please select a receiver before saving to PDF.")
            return

        copies = self.copies_spinbox.value()
        save_widget_as_pdf(self, self.label_preview, copies)

    def on_copies_changed(self, value):
        self.label_preview.update_copy_count(value)

    def load_receiver_data(self):
        receivers = get_all_receiver_identities()
        self.receiver_list_view.populate_table(receivers)

    def load_sender_data(self):
        self.senders_data = get_all_senders()
        self.sender_combo.blockSignals(True)
        self.sender_combo.clear()
        for sender in self.senders_data:
            self.sender_combo.addItem(sender['name'], userData=sender['id'])
        
        default_inventory_code = get_config("bills_process_inventory_code")
        if default_inventory_code:
            for i, sender in enumerate(self.senders_data):
                if sender['inventory_code'] == default_inventory_code:
                    self.sender_combo.setCurrentIndex(i)
                    break
        self.sender_combo.blockSignals(False)
        self.on_sender_selected(self.sender_combo.currentIndex()) # Manually trigger for initial load

    def on_receiver_selected(self, receiver_id):
        if receiver_id > 0:
            # Get receiver identity data from DB
            identity = get_receiver_identity_by_id(receiver_id)
            if not identity:
                self.receiver_name_input.clear()
                self.receiver_tel_input.clear()
                self.receiver_address_input.clear()
                # Clear live view
                self.label_preview.update_receiver_info("Receiver not found", "", "", "")
                return

            # Populate name and tel from the identity data
            self.receiver_name_input.setText(identity.get("name", ""))
            self.receiver_tel_input.setText(identity.get("tel", ""))

            # Get address data from DB
            addresses = get_addresses_for_receiver(receiver_id)
            if not addresses:
                self.receiver_address_input.clear()
                # Clear live view address part
                self.label_preview.update_receiver_info(
                    identity.get("name", "N/A"),
                    "No address found for this receiver.",
                    identity.get('tel', 'N/A'),
                    ""
                )
                return

            # Find the default address or use the first one
            default_address = next((addr for addr in addresses if addr.get('is_default')), addresses[0])
            
            full_address = (
                f"{default_address.get('address_detail', '')} "
                f"ต.{default_address.get('sub_district', '')} "
                f"อ.{default_address.get('district', '')} "
                f"จ.{default_address.get('province', '')} "
                f"{default_address.get('post_code', '')}"
            )
            self.receiver_address_input.setText(full_address)

            # Update live view
            self.label_preview.update_receiver_info(
                identity.get("name", "N/A"),
                full_address,
                identity.get('tel', 'N/A'),
                default_address.get('delivery_by', 'N/A'),
                default_address.get('note', 'N/A')
            )
            self.receiver_delivery_by_input.setText(default_address.get('delivery_by', 'N/A'))
            self.receiver_note_input.setText(default_address.get('note', ''))
        else:
            self.receiver_name_input.clear()
            self.receiver_tel_input.clear()
            self.receiver_address_input.clear()
            self.receiver_delivery_by_input.clear()
            self.receiver_note_input.clear()
            # Clear live view
            self.label_preview.clear_receiver_info()

    def on_sender_selected(self, index):
        if index < 0 or not self.senders_data:
            self.label_preview.clear_sender_info()
            return
        
        sender = self.senders_data[index]
        self.sender_name_input.setText(sender.get('name', ''))
        self.sender_tel_input.setText(sender.get('tel', ''))
        full_address = (
            f"{sender.get('address_detail', '')} "
            f"ต.{sender.get('sub_district', '')} "
            f"อ.{sender.get('district', '')} "
            f"จ.{sender.get('province', '')} "
            f"{sender.get('post_code', '')}"
        )
        self.sender_address_input.setText(full_address)

        # Update live view
        self.label_preview.update_sender_info(
            full_address,
            sender.get('tel', 'N/A')
        )

    def showEvent(self, event):
        super().showEvent(event)
        if self.isVisible():
            self.load_receiver_data()
            self.load_sender_data()
            self.label_preview.refresh_assets()

