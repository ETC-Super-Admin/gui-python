from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QMenu
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
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
        self.filter_methods = [
            "Name", "Tel.", "Inventory", "Delivery By", "Province", 
            "District", "Sub-district", "Post Code", "Zone"
        ]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_layout = self._create_header_layout()
        layout.addLayout(header_layout)

        self.table = self._create_table_widget()
        layout.addWidget(self.table)

    def _create_header_layout(self):
        header_layout = QHBoxLayout()
        
        filter_widget = self._create_filter_widget()
        header_layout.addWidget(filter_widget)

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
        self.import_button.setObjectName("EditUserButton")
        self.import_button.clicked.connect(self.import_requested.emit)
        header_layout.addWidget(self.import_button)

        self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Receiver")
        self.add_button.setObjectName("AddUserButton")
        self.add_button.clicked.connect(self.add_receiver_requested.emit)
        header_layout.addWidget(self.add_button)

        return header_layout

    def _create_filter_widget(self):
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0,0,0,0)
        filter_layout.setSpacing(5)

        search_by_label = QLabel("Search by")
        filter_layout.addWidget(search_by_label)

        self.filter_button = QPushButton(self.filter_methods[0])
        self.filter_button.setObjectName("FilterButton") # For styling
        
        filter_menu = QMenu(self)
        for method in self.filter_methods:
            action = QAction(method, self)
            action.triggered.connect(lambda checked=False, m=method: self._set_filter_by(m))
            filter_menu.addAction(action)
        
        self.filter_button.setMenu(filter_menu)
        filter_layout.addWidget(self.filter_button)

        return filter_widget

    def _set_filter_by(self, method):
        self.filter_button.setText(method)
        self.filter_table() # Re-apply filter when method changes

    def _create_table_widget(self):
        table = QTableWidget()
        table.setObjectName("Card")
        table.setAlternatingRowColors(True)
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "ID", "Inventory", "Name", "Address Details", "Sub-district",
            "District", "Province", "Post Code", "Tel.", "Delivery By", "Zone"
        ])
        
        header = table.horizontalHeader()
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name column
        for i in range(table.columnCount()):
            if i not in [0, 2]:
                header.setSectionResizeMode(i, QHeaderView.Interactive)

        table.setColumnWidth(1, 80); table.setColumnWidth(3, 180); table.setColumnWidth(4, 100)
        table.setColumnWidth(5, 100); table.setColumnWidth(6, 100); table.setColumnWidth(7, 60)
        table.setColumnWidth(8, 100); table.setColumnWidth(9, 100); table.setColumnWidth(10, 80)
        table.setColumnHidden(0, True)

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
            self.table.setItem(row_position, 10, QTableWidgetItem(receiver.get("zone", "")))
        self.clear_selection()
        self.search_input.clear()

    def filter_table(self):
        filter_method = self.filter_button.text()
        search_text = self.search_input.text().lower()

        column_map = {
            "Name": 2, "Tel.": 8, "Inventory": 1, "Delivery By": 9, "Province": 6, 
            "District": 5, "Sub-district": 4, "Post Code": 7, "Zone": 10
        }
        filter_column_index = column_map.get(filter_method)

        if filter_column_index is None:
            return

        for row in range(self.table.rowCount()):
            item = self.table.item(row, filter_column_index)
            is_match = search_text in item.text().lower() if item and item.text() else False
            self.table.setRowHidden(row, not is_match)

    def clear_selection(self):
        self.table.clearSelection()
