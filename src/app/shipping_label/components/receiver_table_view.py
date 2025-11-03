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

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
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
        self.all_receivers_data = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        header_widget = self._create_header_widget()
        layout.addWidget(header_widget)

        self.table = self._create_table_widget()
        layout.addWidget(self.table)

    def _create_header_widget(self):
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        # Filter row
        filter_layout = QHBoxLayout()
        self.filter_field_combo = QComboBox()
        self.filter_field_combo.addItems(["All", "Zone", "Province", "District", "Sub-district", "Post Code"])
        self.filter_value_input = QLineEdit()
        self.filter_value_input.setPlaceholderText("Enter value for selected field...")
        filter_layout.addWidget(self.filter_field_combo)
        filter_layout.addWidget(self.filter_value_input)
        header_layout.addLayout(filter_layout)

        # Name search row
        name_search_layout = QHBoxLayout()
        name_search_layout.addWidget(QLabel("Search:"))
        self.name_search_input = QLineEdit()
        self.name_search_input.setPlaceholderText("Filter results by name or telephone...")
        name_search_layout.addWidget(self.name_search_input)
        header_layout.addLayout(name_search_layout)

        # Connections
        self.filter_field_combo.currentTextChanged.connect(self.apply_filters)
        self.filter_value_input.textChanged.connect(self.apply_filters)
        self.name_search_input.textChanged.connect(self.apply_filters)

        if self.show_add_button:
            add_button_layout = QHBoxLayout()
            add_button_layout.addStretch()
            self.add_button = QPushButton(qta.icon('fa5s.plus', color='white'), " Add Receiver")
            self.add_button.setObjectName("AddUserButton")
            self.add_button.clicked.connect(self.add_receiver_requested.emit)
            add_button_layout.addWidget(self.add_button)
            header_layout.addLayout(add_button_layout)

        return header_widget

    def _create_table_widget(self):
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["ID", "ชื่อ", "โทรศัพท์", "ที่อยู่"])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name column
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
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
        self.all_receivers_data = receivers
        self.apply_filters()

    def apply_filters(self):
        filter_field = self.filter_field_combo.currentText().lower().replace('-', '_').replace(' ', '_')
        filter_value = self.filter_value_input.text().lower().strip()
        name_search = self.name_search_input.text().lower().strip()

        self.table.setRowCount(0)

        for receiver in self.all_receivers_data:
            # Primary filter
            primary_match = False
            if filter_field == 'all' or not filter_value:
                primary_match = True
            else:
                for address in receiver.get('addresses', []):
                    db_value = str(address.get(filter_field, '')).lower().strip()
                    if filter_value in db_value:
                        primary_match = True
                        break
            
            if not primary_match:
                continue

            # Name/Tel filter
            name_match = False
            if not name_search:
                name_match = True
            else:
                if name_search in receiver.get('name', '').lower().strip() or name_search in receiver.get('tel', '').lower().strip():
                    name_match = True

            if name_match:
                # Add row to table
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(str(receiver["id"])))
                self.table.setItem(row_position, 1, QTableWidgetItem(receiver["name"]))
                self.table.setItem(row_position, 2, QTableWidgetItem(receiver.get("tel", "")))
                
                count_item = QTableWidgetItem(str(receiver.get("address_count", 0)))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_position, 3, count_item)

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
