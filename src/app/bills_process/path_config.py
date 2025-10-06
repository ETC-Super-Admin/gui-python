from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFormLayout, QGroupBox, QFileDialog
from PySide6.QtCore import Qt
import qtawesome as qta

class PathConfig(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Page Title
        title_label = QLabel("Path Configuration")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Configuration Form
        form_groupbox = QGroupBox("")  # no visible title
        form_groupbox.setObjectName("Card")
        form_layout = QFormLayout(form_groupbox)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)


        # Template Directory Input
        self.template_dir_input = QLineEdit()
        self.template_dir_input.setPlaceholderText("Select the template directory")
        self.template_dir_input.setReadOnly(True)
        browse_button = QPushButton(qta.icon('fa5s.folder-open', color='#64748b'), " Browse...")
        browse_button.setObjectName("CancelFormButton") # Re-use a neutral style
        browse_button.clicked.connect(self.browse_template_directory)

        template_dir_layout = QHBoxLayout()
        template_dir_layout.addWidget(self.template_dir_input)
        template_dir_layout.addWidget(browse_button)
        form_layout.addRow("Template Directory:", template_dir_layout)

        # Inventory Code Input
        self.inventory_code_input = QLineEdit()
        self.inventory_code_input.setPlaceholderText("Enter inventory code ex: BKK")
        form_layout.addRow("Inventory Code:", self.inventory_code_input)

        main_layout.addWidget(form_groupbox)

        # Save Button
        save_button_layout = QHBoxLayout()
        self.save_button = QPushButton(qta.icon('fa5s.save', color='white'), " Save Configuration")
        self.save_button.setObjectName("SaveUserButton") # Re-use a primary action style
        self.save_button.clicked.connect(self.save_configuration)
        save_button_layout.addStretch()
        save_button_layout.addWidget(self.save_button)
        main_layout.addLayout(save_button_layout)


        main_layout.addStretch()

    def browse_template_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Template Directory")
        if directory:
            self.template_dir_input.setText(directory)

    def save_configuration(self):
        template_dir = self.template_dir_input.text()
        inventory_code = self.inventory_code_input.text()
        print(f"Saving configuration: Template Dir='{template_dir}', Inventory Code='{inventory_code}'")
        # In a real implementation, this would save to QSettings or a config file
        pass