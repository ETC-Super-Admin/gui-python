from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Profile(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        label = QLabel("Profile Page")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
        layout.addStretch()
