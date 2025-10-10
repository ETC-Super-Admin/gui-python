from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, 
    QFormLayout, QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
import qtawesome as qta

# Import DB queries for saving/loading config
from src.db.config_queries import save_config, get_config

class LabelAsset(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_saved_assets()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)

        title_label = QLabel("Label Asset Management")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # --- Form for managing assets ---
        form_groupbox = QGroupBox("Image Assets")
        form_groupbox.setObjectName("Card")
        form_layout = QFormLayout(form_groupbox)
        form_layout.setSpacing(15)

        # --- Sender Asset Input ---
        self.sender_asset_input = QLineEdit()
        self.sender_asset_input.setPlaceholderText("No logo selected")
        self.sender_asset_input.setReadOnly(True)
        
        sender_browse_button = QPushButton(qta.icon('fa5s.folder-open', color='#64748b'), " Browse...")
        sender_browse_button.setObjectName("CancelFormButton") # Re-use style
        sender_browse_button.clicked.connect(self.browse_sender_asset)

        sender_layout = QHBoxLayout()
        sender_layout.addWidget(self.sender_asset_input)
        sender_layout.addWidget(sender_browse_button)
        form_layout.addRow("Sender Logo (e.g., Company Logo):", sender_layout)

        # --- Receiver Asset Input ---
        self.receiver_asset_input = QLineEdit()
        self.receiver_asset_input.setPlaceholderText("No logo selected")
        self.receiver_asset_input.setReadOnly(True)

        receiver_browse_button = QPushButton(qta.icon('fa5s.folder-open', color='#64748b'), " Browse...")
        receiver_browse_button.setObjectName("CancelFormButton") # Re-use style
        receiver_browse_button.clicked.connect(self.browse_receiver_asset)

        receiver_layout = QHBoxLayout()
        receiver_layout.addWidget(self.receiver_asset_input)
        receiver_layout.addWidget(receiver_browse_button)
        form_layout.addRow("Receiver Logo (e.g., Fragile Icon):", receiver_layout)

        main_layout.addWidget(form_groupbox)

        # --- Action Buttons ---
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save Assets")
        self.save_button.setObjectName("SaveUserButton")
        self.save_button.clicked.connect(self.save_assets)
        action_layout.addWidget(self.save_button)

        main_layout.addLayout(action_layout)

    def browse_sender_asset(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Sender Logo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.svg)"
        )
        if file_path:
            self.sender_asset_input.setText(file_path)

    def browse_receiver_asset(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Receiver Logo", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.svg)"
        )
        if file_path:
            self.receiver_asset_input.setText(file_path)

    def load_saved_assets(self):
        sender_logo_path = get_config("asset_sender_logo", "")
        receiver_logo_path = get_config("asset_receiver_logo", "")
        self.sender_asset_input.setText(sender_logo_path)
        self.receiver_asset_input.setText(receiver_logo_path)

    def save_assets(self):
        sender_path = self.sender_asset_input.text()
        receiver_path = self.receiver_asset_input.text()

        save_config("asset_sender_logo", sender_path)
        save_config("asset_receiver_logo", receiver_path)

        QMessageBox.information(self, "Success", "Asset paths have been saved successfully.")

    def showEvent(self, event):
        """Override showEvent to refresh data when the widget is shown."""
        super().showEvent(event)
        if self.isVisible():
            self.load_saved_assets()
