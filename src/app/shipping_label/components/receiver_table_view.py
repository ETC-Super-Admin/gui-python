from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QHBoxLayout, QComboBox, QLineEdit, QPushButton
)
from PySide6.QtCore import Signal
import qtawesome as qta

class ReceiverTableView(QWidget):
    """
    A widget that displays a filterable table of receivers.
    It handles the table UI, filtering, and emits signals for user actions.
    """
    add_receiver_requested = Signal()
    edit_receiver_requested = Signal(int)  # Emits receiver ID
    import_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header with filter and action buttons
        header_layout = self._create_header_layout()
        layout.addLayout(header_layout)

        # Table widget
        self.table = self._create_table_widget()
        layout.addWidget(self.table)

    def _create_header_layout(self):
        header_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Search by Name", "Search by Tel.", "Search by Inventory", "Search by Delivery By",
            "Search by Province", "Search by District", "Search by Sub-district", "Search by Post Code"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        header_layout.addWidget(self.filter_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search table...")
        self.search_input.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search_input)

        header_layout.addStretch()

        self.export_button = QPushButton(qta.icon('fa5s.file-export', color='white'), " Export Excel")
        self.export_button.setObjectName("ExportButton")
        self.export_button.clicked.connect(self.export_requested.emit)
        header_layout.addWidget(self.export_button)

        self.import_button = QPushButton(qta.icon('fa5s.file-import', color='white'), " Import Excel")
        self.import_button.setObjectName("EditUserButton")  # Re-use amber style
        self.import_button.clicked.connect(self.import_requested.emit)
        header_layout.addWidget(self.import_button)

        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Receiver")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.add_receiver_requested.emit)
        header_layout.addWidget(self.add_button)

        return header_layout

    def _create_table_widget(self):
        table = QTableWidget()
        table.setObjectName("Card")
        table.setAlternatingRowColors(True)
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "ID", "Inventory", "Name", "Address Details", "Sub-district",
            "District", "Province", "Post Code", "Tel.", "Delivery By"
        ])
        
        header = table.horizontalHeader()
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name column
        for i in range(table.columnCount()):
            if i not in [0, 2]:  # Skip ID and Name
                header.setSectionResizeMode(i, QHeaderView.Interactive)

        table.setColumnWidth(1, 80)    # Inventory
        table.setColumnWidth(3, 180)   # Address Details
        table.setColumnWidth(4, 100)   # Sub-district
        table.setColumnWidth(5, 100)   # District
        table.setColumnWidth(6, 100)   # Province
        table.setColumnWidth(7, 60)    # Post Code
        table.setColumnWidth(8, 100)   # Tel
        table.setColumnWidth(9, 100)   # Delivery By
        table.setColumnHidden(0, True) # Hide ID

        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        return table

    def _on_selection_changed(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            receiver_id = int(self.table.item(selected_items[0].row(), 0).text())
            self.edit_receiver_requested.emit(receiver_id)

    def populate_table(self, receivers):
        self.table.setRowCount(0)
        for receiver in receivers:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(receiver["id"])))
            self.table.setItem(row_position, 1, QTableWidgetItem(receiver["inventory_code"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(receiver["name"]))
            self.table.setItem(row_position, 3, QTableWidgetItem(receiver.get("address_detail", "")))
            self.table.setItem(row_position, 4, QTableWidgetItem(receiver.get("sub_district", "")))
            self.table.setItem(row_position, 5, QTableWidgetItem(receiver.get("district", "")))
            self.table.setItem(row_position, 6, QTableWidgetItem(receiver.get("province", "")))
            self.table.setItem(row_position, 7, QTableWidgetItem(receiver["post_code"]))
            self.table.setItem(row_position, 8, QTableWidgetItem(receiver["tel"]))
            self.table.setItem(row_position, 9, QTableWidgetItem(receiver["delivery_by"]))
        self.clear_selection()
        self.search_input.clear()

    def filter_table(self):
        filter_column_text = self.filter_combo.currentText()
        search_text = self.search_input.text().lower()

        column_map = {
            "Search by Name": 2, "Search by Tel.": 8, "Search by Inventory": 1,
            "Search by Delivery By": 9, "Search by Province": 6, "Search by District": 5,
            "Search by Sub-district": 4, "Search by Post Code": 7
        }
        filter_column_index = column_map.get(filter_column_text)

        if filter_column_index is None:
            return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, filter_column_index)
            is_match = search_text in item.text().lower() if item else False
            self.table.setRowHidden(row, not is_match)

    def clear_selection(self):
        self.table.clearSelection()
