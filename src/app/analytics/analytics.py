from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Analytics(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Analytics Page")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
