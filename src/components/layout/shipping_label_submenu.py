import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .sidebar_buttons import create_nav_button

class ShippingLabelSubMenu(QWidget):
    sub_page_changed = Signal(str)

    def __init__(self, parent=None, create_nav_button_func=None):
        super().__init__(parent)
        self.setObjectName("ShippingLabelSubMenu")
        self.create_nav_button = create_nav_button_func

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.overview_button = self.create_nav_button(
            qta.icon('fa5s.barcode', color='#64748b'),
            "Overview",
            is_sub_button=True
        )
        layout.addWidget(self.overview_button)
        self.overview_button.clicked.connect(lambda: self.sub_page_changed.emit("shipping_label"))

        self.label_asset_button = self.create_nav_button(
            qta.icon('fa5s.box', color='#64748b'),
            "Label Asset",
            is_sub_button=True
        )
        layout.addWidget(self.label_asset_button)
        self.label_asset_button.clicked.connect(lambda: self.sub_page_changed.emit("label_asset"))

        self.sender_management_button = self.create_nav_button(
            qta.icon('fa5s.user-check', color='#64748b'),
            "Sender Management",
            is_sub_button=True
        )
        layout.addWidget(self.sender_management_button)
        self.sender_management_button.clicked.connect(lambda: self.sub_page_changed.emit("sender_management"))

        self.receiver_management_button = self.create_nav_button(
            qta.icon('fa5s.user-tag', color='#64748b'),
            "Receiver Management",
            is_sub_button=True
        )
        layout.addWidget(self.receiver_management_button)
        self.receiver_management_button.clicked.connect(lambda: self.sub_page_changed.emit("receiver_management"))

        self.sub_buttons = {
            "shipping_label": self.overview_button,
            "label_asset": self.label_asset_button,
            "sender_management": self.sender_management_button,
            "receiver_management": self.receiver_management_button,
        }
