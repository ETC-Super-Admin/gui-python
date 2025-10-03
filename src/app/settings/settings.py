from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Settings(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        label = QLabel("Settings Page")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
        layout.addStretch()
