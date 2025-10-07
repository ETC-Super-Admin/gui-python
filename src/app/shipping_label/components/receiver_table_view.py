from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QHBoxLayout, QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt
import qtawesome as qta

class ReceiverTableView(QWidget):
    """
    A widget that displays a filterable table of receiver identities.
    It handles the table UI, filtering, and emits signals for user actions.
    """
    add_receiver_requested = Signal()
    receiver_selected = Signal(int)  # Emits receiver identity ID

    def __init__(self, parent=None, show_add_button=True):
        super().__init__(parent)
        self.show_add_button = show_add_button
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
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search_input)

        if self.show_add_button:
            self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Receiver")
            self.add_button.setObjectName("AddUserButton")
            self.add_button.clicked.connect(self.add_receiver_requested.emit)
            header_layout.addWidget(self.add_button)

        return header_layout

    def _create_table_widget(self):
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ID", "Name", "Addresses"])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
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
            self.receiver_selected.emit(receiver_id)
        else:
            self.receiver_selected.emit(-1)

    def populate_table(self, receivers):
        self.table.setRowCount(0)
        for receiver in receivers:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(receiver["id"])))
            self.table.setItem(row_position, 1, QTableWidgetItem(receiver["name"]))
            
            count_item = QTableWidgetItem(str(receiver.get("address_count", 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_position, 2, count_item)

        self.clear_selection()
        self.search_input.clear()

    def filter_table(self):
        search_text = self.search_input.text().lower()

        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            
            name_match = search_text in name_item.text().lower() if name_item and name_item.text() else False
            
            self.table.setRowHidden(row, not name_match)

    def clear_selection(self):
        self.table.clearSelection()

    def select_row_by_id(self, receiver_id):
        if receiver_id is None:
            self.clear_selection()
            return
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == receiver_id:
                self.table.selectRow(row)
                return
