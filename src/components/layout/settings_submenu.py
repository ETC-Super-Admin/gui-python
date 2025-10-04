import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .sidebar_buttons import create_nav_button # Changed to relative import

class SettingsSubMenu(QWidget):
    sub_page_changed = Signal(str)

    def __init__(self, parent=None, create_nav_button_func=None, user_role="user"):
        super().__init__(parent)
        self.setObjectName("SettingsSubMenu")
        self.create_nav_button = create_nav_button_func
        self.user_role = user_role

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.general_settings_button = self.create_nav_button(
            qta.icon('fa5s.sliders-h', color='#64748b'),
            "General",
            is_sub_button=True
        )
        layout.addWidget(self.general_settings_button)

        if self.user_role == 'admin':
            pass # User Management moved to Admin submenu

        self.sub_buttons = {
            "general_settings": self.general_settings_button,
        }

        self.general_settings_button.clicked.connect(lambda: self.sub_page_changed.emit("general_settings"))
