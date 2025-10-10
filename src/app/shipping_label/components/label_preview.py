from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from src.db.config_queries import get_config
import os

class LabelPreview(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LabelPreview")
        self._setup_ui()
        self.load_and_display_assets()

    def _setup_ui(self):
        display_width = 591
        display_height = 394

        self.setStyleSheet("""
            #LabelPreview { 
                border: 2px dashed #ef4444; 
                background-color: white; 
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        self.setFixedSize(display_width, display_height)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        sender_info_widget = self._create_label_section("FROM", "sender")
        
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #e2e8f0;")

        receiver_info_widget = self._create_label_section("TO", "receiver")

        main_layout.addWidget(sender_info_widget, 4)
        main_layout.addWidget(separator)
        main_layout.addWidget(receiver_info_widget, 6)

    def _create_label_section(self, title, prefix):
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0,0,0,0)
        section_layout.setSpacing(5)
        section_layout.setAlignment(Qt.AlignTop)

        asset_label = QLabel()
        asset_label.setAlignment(Qt.AlignCenter)
        if prefix == "receiver":
            asset_label.setMaximumHeight(120) # Larger height for receiver
        else:
            asset_label.setMaximumHeight(60) # Original height for sender
        setattr(self, f"{prefix}_asset_label", asset_label)
        section_layout.addWidget(asset_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #64748b; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; margin-bottom: 5px;")
        section_layout.addWidget(title_label)

        if prefix == "receiver":
            name_label = QLabel("Name will appear here")
            name_label.setWordWrap(True)
            name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
            setattr(self, f"{prefix}_name_label", name_label)
            section_layout.addWidget(name_label)

        address_label = QLabel("Full address will appear here")
        address_label.setWordWrap(True)
        address_label.setStyleSheet("font-size: 14px; color: #334155;")
        setattr(self, f"{prefix}_address_label", address_label)
        section_layout.addWidget(address_label)

        tel_label = QLabel("Tel: ...")
        tel_label.setWordWrap(True)
        tel_label.setStyleSheet("font-size: 14px; color: #334155; font-weight: bold;")
        setattr(self, f"{prefix}_tel_label", tel_label)
        section_layout.addWidget(tel_label)

        section_layout.addStretch()

        if prefix == "sender":
            self.copy_count_label = QLabel("1/1")
            self.copy_count_label.setAlignment(Qt.AlignLeft)
            self.copy_count_label.setStyleSheet("font-size: 14px; color: #64748b; font-weight: bold;")
            section_layout.addWidget(self.copy_count_label)

        return section_widget

    def load_and_display_assets(self):
        sender_path = get_config("asset_sender_logo", "")
        if sender_path and os.path.exists(sender_path):
            pixmap = QPixmap(sender_path)
            self.sender_asset_label.setPixmap(pixmap.scaled(
                self.sender_asset_label.width(),
                self.sender_asset_label.maximumHeight(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.sender_asset_label.clear()

        receiver_path = get_config("asset_receiver_logo", "")
        if receiver_path and os.path.exists(receiver_path):
            pixmap = QPixmap(receiver_path)
            self.receiver_asset_label.setPixmap(pixmap.scaled(
                self.receiver_asset_label.width(),
                self.receiver_asset_label.maximumHeight(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.receiver_asset_label.clear()

    def refresh_assets(self):
        self.load_and_display_assets()

    def update_sender_info(self, address, tel):
        self.sender_address_label.setText(address or "")
        self.sender_tel_label.setText(f"Tel: {tel or 'N/A'}")

    def update_receiver_info(self, name, address, tel):
        self.receiver_name_label.setText(name or "N/A")
        self.receiver_address_label.setText(address or "")
        self.receiver_tel_label.setText(f"Tel: {tel or 'N/A'}")

    def update_copy_count(self, total):
        self.copy_count_label.setText(f"1/{total}")

    def clear_sender_info(self):
        self.update_sender_info("Select a sender", "")

    def clear_receiver_info(self):
        self.update_receiver_info("TO", "Select a receiver from the list", "")
