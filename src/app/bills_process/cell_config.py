from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CellConfig(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 4, 20, 4)
        label = QLabel("Cell Config Page")
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
        layout.addStretch()
