import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .sidebar_buttons import create_nav_button # Changed to relative import

class SettingsSubMenu(QWidget):
    sub_page_changed = Signal(str)

    def __init__(self, parent=None, create_nav_button_func=None):
        super().__init__(parent)
        self.setObjectName("SettingsSubMenu")
        self.create_nav_button = create_nav_button_func

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.general_settings_button = self.create_nav_button(
            qta.icon('fa5s.sliders-h', color='#64748b'),
            "General",
            is_sub_button=True
        )
        self.user_management_button = self.create_nav_button(
            qta.icon('fa5s.users', color='#64748b'),
            "Users",
            is_sub_button=True
        )

        layout.addWidget(self.general_settings_button)
        layout.addWidget(self.user_management_button)

        self.sub_buttons = {
            "general_settings": self.general_settings_button,
            "user_management": self.user_management_button,
        }

        self.general_settings_button.clicked.connect(lambda: self.sub_page_changed.emit("general_settings"))
        self.user_management_button.clicked.connect(lambda: self.sub_page_changed.emit("user_management"))
