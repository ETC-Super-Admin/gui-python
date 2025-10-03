from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Projects(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Projects Page")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
