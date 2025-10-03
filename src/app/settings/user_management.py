from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class UserManagement(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("User Management Page")
        label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(label)
