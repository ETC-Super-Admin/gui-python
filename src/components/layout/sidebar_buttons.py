import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap


def create_nav_button(icon, text, is_sub_button=False):
    button = QPushButton(icon, f"  {text}")
    button.setObjectName("SidebarButton")
    button.setCheckable(True)
    button.setFixedHeight(45)
    button.setCursor(Qt.PointingHandCursor)
    
    font = QFont()
    font.setPointSize(10)
    button.setFont(font)

    if is_sub_button:
        button.setStyleSheet("padding-left: 45px;")
    
    return button


def create_expandable_button(icon_name_str, text, toggle_function, theme_manager):
    """Create a button with an expandable chevron indicator"""
    container = QWidget()
    container.setObjectName("SidebarButton")
    container.setCursor(Qt.PointingHandCursor)
    container.setFixedHeight(45)
    
    # Make container clickable
    container.mousePressEvent = lambda e: toggle_function()
    
    layout = QHBoxLayout(container)
    layout.setContentsMargins(15, 0, 15, 0)
    layout.setSpacing(10)
    
    # Main icon
    settings_icon_label = QLabel()
    settings_icon_label.setPixmap(qta.icon(icon_name_str, color='#64748b').pixmap(16, 16))
    layout.addWidget(settings_icon_label)
    
    # Text label
    text_label = QLabel(text)
    text_label.setObjectName("ButtonText")
    font = QFont()
    font.setPointSize(10)
    font.setWeight(QFont.Medium)
    text_label.setFont(font)
    layout.addWidget(text_label)
    
    layout.addStretch()
    
    # Chevron icon
    chevron_label = QLabel()
    chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
    chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
    layout.addWidget(chevron_label)
    
    # Store references
    container.setCheckable = lambda x: None  # Dummy method for compatibility
    container.setChecked = lambda x: update_expandable_button_state(container, x, theme_manager, settings_icon_label, chevron_label, icon_name_str)
    container.isChecked = lambda: False # This will be handled by the parent
    
    return container, settings_icon_label, chevron_label


def update_expandable_button_state(container, checked, theme_manager, settings_icon_label, chevron_label, icon_name_str):
    """Update the visual state of expandable button"""
    current_theme = theme_manager.get_current_theme_colors()
    
    if checked:
        container.setStyleSheet(f"""
            background-color: {current_theme["PRIMARY"]};
            border-radius: 8px;
        """)
        icon_color = current_theme["PRIMARY_FOREGROUND"]
    else:
        container.setStyleSheet("""
            background-color: transparent;
            border-radius: 8px;
        """)
        icon_color = '#64748b'
    
    # Update main icon
    settings_icon = qta.icon(icon_name_str, color=icon_color)
    settings_icon_label.setPixmap(settings_icon.pixmap(16, 16))
    
    # Update text color
    text_label = container.findChild(QLabel, "ButtonText")
    if text_label:
        text_label.setStyleSheet(f"color: {icon_color};")

    # Update chevron color
    if checked:
        chevron_icon = qta.icon('fa5s.chevron-up', color=icon_color)
    else:
        chevron_icon = qta.icon('fa5s.chevron-down', color=icon_color)
    chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
