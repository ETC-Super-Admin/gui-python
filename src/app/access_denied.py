from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AccessDenied(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 4, 20, 4)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("&#x1F6AB;") # No Entry Sign emoji
        icon_label.setStyleSheet("font-size: 80px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel("Access Denied")
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #ef4444;") # Tailwind red-500
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        message_label = QLabel("You do not have permission to view this page.")
        message_label.setStyleSheet("font-size: 18px; color: #64748b;") # Tailwind slate-500
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)

        layout.addStretch()