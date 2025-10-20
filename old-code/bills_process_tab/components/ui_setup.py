# src/components/tabs/bills_process_tab/components/ui_setup.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton, QSizePolicy, QDateEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate
from src.styles.theme import ModernTheme

def setup_ui(parent_widget):
    """Setup the main UI layout for the bills process tab."""
    main_layout = QHBoxLayout(parent_widget)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    # Left side: Log display panel
    left_panel = _create_left_panel(parent_widget)
    
    # Right side: Controls
    right_panel = _create_right_panel(parent_widget)
    
    # Add left and right panels to main layout (70:30 ratio)
    main_layout.addWidget(left_panel, 7)
    main_layout.addWidget(right_panel, 3)
    
    return main_layout

def _create_left_panel(parent_widget):
    """Create the left panel with log display."""
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(10)
    
    log_label = QLabel("Bills Processing Log")
    log_label.setFont(QFont("Arial", 14, QFont.Bold))
    
    parent_widget.log_display = QTextEdit()
    parent_widget.log_display.setReadOnly(True)
    parent_widget.log_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    left_layout.addWidget(log_label)
    left_layout.addWidget(parent_widget.log_display)
    
    left_panel.setMinimumWidth(400)
    left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    return left_panel

def _create_right_panel(parent_widget):
    """Create the right panel with controls."""
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(8)
    
    # Date selection
    date_label = QLabel("Select Date")
    parent_widget.date_input = QDateEdit()
    parent_widget.date_input.setDisplayFormat("dd/MM/yyyy")
    parent_widget.date_input.setCalendarPopup(True)
    parent_widget.date_input.setDate(QDate.currentDate())

    parent_widget.unmerge_btn = QPushButton("ยกเลิกรวมเซลล์")
    parent_widget.unmerge_btn.setStyleSheet(ModernTheme.get_button_stylesheet("light"))
    parent_widget.unmerge_btn.setMinimumHeight(32)

    parent_widget.process_template_btn = QPushButton("📂 ประมวลผลไฟล์")
    parent_widget.process_template_btn.setStyleSheet(ModernTheme.get_button_stylesheet("success"))
    parent_widget.process_template_btn.setMinimumHeight(32)

    # Custom blue hover/pressed for light variant
    custom_colors = {
        'hover': '#a78bfa',      # Blue hover
        'pressed': '#7e22ce',    # Darker blue pressed
        'hover_text': 'white',   # White text on hover
        'pressed_text': 'white'  # White text on pressed
    }
    parent_widget.update_formula_btn = QPushButton("อัปเดตสูตร")
    parent_widget.update_formula_btn.setStyleSheet(ModernTheme.get_button_stylesheet("light", custom_colors))
    parent_widget.update_formula_btn.setMinimumHeight(32)

    parent_widget.open_file_btn = QPushButton("เปิดไฟล์")
    parent_widget.open_file_btn.setStyleSheet(ModernTheme.get_button_stylesheet("info"))
    parent_widget.open_file_btn.setMinimumHeight(32)

    parent_widget.rearrange_btn = QPushButton("จัดเรียงแถวใหม่")
    parent_widget.rearrange_btn.setStyleSheet(ModernTheme.get_button_stylesheet("warning"))
    parent_widget.rearrange_btn.setMinimumHeight(32)

    parent_widget.clear_cache_btn = QPushButton("ล้างแคชการประมวลผล")
    parent_widget.clear_cache_btn.setStyleSheet(ModernTheme.get_button_stylesheet("danger"))
    parent_widget.clear_cache_btn.setMinimumHeight(32)
    
    # Create a container for main action buttons
    buttons_container = QWidget()
    buttons_layout = QVBoxLayout(buttons_container)
    buttons_layout.setContentsMargins(0, 0, 0, 0)
    buttons_layout.setSpacing(8)
    
    # Add date selector and main action buttons to top container
    right_layout.addWidget(date_label)
    right_layout.addWidget(parent_widget.date_input)
    right_layout.addSpacing(10)
    
    # Group main action buttons
    buttons_layout.addWidget(parent_widget.unmerge_btn)
    buttons_layout.addWidget(parent_widget.process_template_btn)
    buttons_layout.addWidget(parent_widget.update_formula_btn)
    buttons_layout.addSpacing(18)
    buttons_layout.addWidget(parent_widget.rearrange_btn)
    buttons_layout.addWidget(parent_widget.open_file_btn)
    
    # Add buttons container and stretch to create space
    right_layout.addWidget(buttons_container)
    right_layout.addStretch()
    
    # Add clear cache button at the bottom
    right_layout.addWidget(parent_widget.clear_cache_btn)
    
    right_panel.setMaximumWidth(250)
    right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    
    return right_panel