from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class Footer(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Footer")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        footer_label = QLabel("© 2025 Jira Inspired App")
        footer_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(footer_label, alignment=Qt.AlignCenter)
