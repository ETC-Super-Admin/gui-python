from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
import qtawesome as qta

class Navbar(QWidget):
    sidebar_toggled = Signal()

    def __init__(self, theme_manager):
        super().__init__()
        self.setObjectName("Navbar")
        self.theme_manager = theme_manager
        self.is_dark_theme = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.sidebar_toggle_button = QPushButton("")
        self.sidebar_toggle_button.clicked.connect(self.sidebar_toggled)
        layout.addWidget(self.sidebar_toggle_button)
        self.update_sidebar_toggle_icon(True) # Assuming sidebar is open initially

        title = QLabel("Jira Inspired App")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        layout.addStretch()

        self.theme_button = QPushButton(qta.icon('fa5s.moon'), "")
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)

    def toggle_theme(self):
        if self.is_dark_theme:
            self.theme_manager.set_light_theme()
            self.theme_button.setIcon(qta.icon('fa5s.moon'))
        else:
            self.theme_manager.set_dark_theme()
            self.theme_button.setIcon(qta.icon('fa5s.sun'))
        self.is_dark_theme = not self.is_dark_theme

    def update_sidebar_toggle_icon(self, is_expanded):
        if is_expanded:
            self.sidebar_toggle_button.setIcon(qta.icon('fa5s.arrow-left'))
        else:
            self.sidebar_toggle_button.setIcon(qta.icon('fa5s.bars'))
