from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
import qtawesome as qta

class CustomSpinBox(QWidget):
    valueChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CustomSpinBox")

        self._minimum = 1
        self._maximum = 999
        self._value = 1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.minus_button = QPushButton(qta.icon('fa5s.minus', color='#64748b'), "")
        self.minus_button.setObjectName("MinusSpinBoxButton")
        
        self.line_edit = QLineEdit(str(self._value))
        self.line_edit.setObjectName("SpinBoxLineEdit")
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.setValidator(QIntValidator(self._minimum, self._maximum, self))

        self.plus_button = QPushButton(qta.icon('fa5s.plus', color='#64748b'), "")
        self.plus_button.setObjectName("PlusSpinBoxButton")

        layout.addWidget(self.line_edit, 1) # Allow line edit to stretch
        layout.addWidget(self.plus_button)
        layout.addWidget(self.minus_button)

        self.minus_button.clicked.connect(self.decrement)
        self.plus_button.clicked.connect(self.increment)
        self.line_edit.textChanged.connect(self._on_text_changed)

    def value(self):
        return self._value

    def setValue(self, value):
        if self._minimum <= value <= self._maximum:
            if self._value == value: return
            self._value = value
            self.line_edit.setText(str(self._value))
            self.valueChanged.emit(self._value)

    def setMinimum(self, value):
        self._minimum = value
        validator = self.line_edit.validator()
        if validator:
            validator.setBottom(value)

    def setMaximum(self, value):
        self._maximum = value
        validator = self.line_edit.validator()
        if validator:
            validator.setTop(value)

    def increment(self):
        self.setValue(self._value + 1)

    def decrement(self):
        self.setValue(self._value - 1)

    def _on_text_changed(self, text):
        if text and text.isdigit():
            val = int(text)
            if self._minimum <= val <= self._maximum:
                if self._value != val:
                    self._value = val
                    self.valueChanged.emit(self._value)
