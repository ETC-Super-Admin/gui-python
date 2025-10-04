from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QGroupBox
from PySide6.QtCore import QDate

class BillsProcess(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left side (70%)
        left_widget = QGroupBox("Bill Details")
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Content for the left side will go here."))
        left_layout.addStretch()

        # Right side (30%)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)

        # Right side - Top Actions
        top_right_group = QGroupBox("Actions")
        top_right_layout = QVBoxLayout(top_right_group)
        top_right_layout.setSpacing(10)

        date_label = QLabel("Select Date:")
        top_right_layout.addWidget(date_label)
        
        date_select = QDateEdit(QDate.currentDate())
        date_select.setCalendarPopup(True)
        date_select.setFixedHeight(35)
        top_right_layout.addWidget(date_select)

        top_right_layout.addSpacing(15)

        button1 = QPushButton("Action 1")
        button2 = QPushButton("Action 2")
        button3 = QPushButton("Action 3")
        button4 = QPushButton("Action 4")
        button5 = QPushButton("Action 5")
        
        top_right_layout.addWidget(button1)
        top_right_layout.addWidget(button2)
        top_right_layout.addWidget(button3)
        top_right_layout.addWidget(button4)
        top_right_layout.addWidget(button5)
        top_right_layout.addStretch()
        
        right_layout.addWidget(top_right_group)

        # Right side - Bottom Finalize
        bottom_right_group = QGroupBox("Finalize")
        bottom_right_layout = QVBoxLayout(bottom_right_group)
        
        finalize_button = QPushButton("Finalize Bill")
        finalize_button.setObjectName("SaveUserButton") # Example of re-using a style
        bottom_right_layout.addWidget(finalize_button)

        right_layout.addWidget(bottom_right_group)

        right_widget.setMaximumWidth(300)
        
        # Add main widgets to layout with stretch factors
        main_layout.addWidget(left_widget, 7)
        main_layout.addWidget(right_widget, 3)