import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .sidebar_buttons import create_nav_button

class AdminSubMenu(QWidget):
    sub_page_changed = Signal(str)

    def __init__(self, parent=None, create_nav_button_func=None):
        super().__init__(parent)
        self.setObjectName("AdminSubMenu")
        self.create_nav_button = create_nav_button_func

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.user_management_button = self.create_nav_button(
            qta.icon('fa5s.users', color='#64748b'),
            "User Management",
            is_sub_button=True
        )
        layout.addWidget(self.user_management_button)
        self.user_management_button.clicked.connect(lambda: self.sub_page_changed.emit("user_management"))

        self.timesheets_button = self.create_nav_button(
            qta.icon('fa5s.clock', color='#64748b'),
            "Timesheets",
            is_sub_button=True
        )
        layout.addWidget(self.timesheets_button)
        self.timesheets_button.clicked.connect(lambda: self.sub_page_changed.emit("timesheets"))

        self.sub_buttons = {
            "user_management": self.user_management_button,
            "timesheets": self.timesheets_button,
        }