from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout
from PySide6.QtCore import Signal, Qt

class ValidatedLineEdit(QWidget):
    validation_changed = Signal(bool)

    def __init__(self, placeholder_text="", validation_func=None, echo_mode=QLineEdit.Normal, toggle_button=None, parent=None):
        super().__init__(parent)
        self.validation_func = validation_func
        self.is_valid = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0,0,0,0)
        input_layout.setSpacing(5)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder_text)
        self.line_edit.setFixedHeight(35)
        self.line_edit.setEchoMode(echo_mode)
        self.line_edit.textChanged.connect(self._validate_input)
        self.line_edit.editingFinished.connect(self._validate_input)
        input_layout.addWidget(self.line_edit)

        if toggle_button:
            input_layout.addWidget(toggle_button)

        self.main_layout.addLayout(input_layout)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ef4444; font-size: 10px;") # Tailwind red-500
        self.error_label.setAlignment(Qt.AlignLeft)
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

        self._validate_input(self.line_edit.text()) # Initial validation

    def _validate_input(self, text=None):
        if text is None:
            text = self.line_edit.text()

        if self.validation_func:
            is_valid, error_message = self.validation_func(text)
            self.is_valid = is_valid
            if not is_valid:
                self.error_label.setText(error_message)
                self.error_label.show()
                self.line_edit.setStyleSheet("border: 1px solid #ef4444;") # Red border
            else:
                self.error_label.hide()
                self.line_edit.setStyleSheet("") # Reset border
        else:
            self.is_valid = True
            self.error_label.hide()
            self.line_edit.setStyleSheet("")
        self.validation_changed.emit(self.is_valid)

    def text(self):
        return self.line_edit.text()

    def setPlaceholderText(self, text):
        self.line_edit.setPlaceholderText(text)

    def setEchoMode(self, mode):
        self.line_edit.setEchoMode(mode)

    def isValid(self):
        return self.is_valid

    def setStyleSheet(self, style_sheet):
        self.line_edit.setStyleSheet(style_sheet)

    def setEnabled(self, enabled):
        self.line_edit.setEnabled(enabled)
        self.error_label.setEnabled(enabled)

    def clear(self):
        self.line_edit.clear()

    def setFocus(self):
        self.line_edit.setFocus()
