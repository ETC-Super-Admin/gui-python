import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .sidebar_buttons import create_nav_button

class BillsProcessSubMenu(QWidget):
    sub_page_changed = Signal(str)

    def __init__(self, parent=None, create_nav_button_func=None):
        super().__init__(parent)
        self.setObjectName("BillsProcessSubMenu")
        self.create_nav_button = create_nav_button_func

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.overview_button = self.create_nav_button(
            qta.icon('fa5s.file-alt', color='#64748b'),
            "Overview",
            is_sub_button=True
        )
        layout.addWidget(self.overview_button)
        self.overview_button.clicked.connect(lambda: self.sub_page_changed.emit("bills_process"))

        self.cell_config_button = self.create_nav_button(
            qta.icon('fa5s.th', color='#64748b'), # 'th' for cells/grid
            "Cell Config",
            is_sub_button=True
        )
        layout.addWidget(self.cell_config_button)
        self.cell_config_button.clicked.connect(lambda: self.sub_page_changed.emit("cell_config"))

        self.path_config_button = self.create_nav_button(
            qta.icon('fa5s.folder-open', color='#64748b'),
            "Path Config",
            is_sub_button=True
        )
        layout.addWidget(self.path_config_button)
        self.path_config_button.clicked.connect(lambda: self.sub_page_changed.emit("path_config"))

        self.sub_buttons = {
            "bills_process": self.overview_button,
            "cell_config": self.cell_config_button,
            "path_config": self.path_config_button,
        }
