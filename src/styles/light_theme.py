from src.styles.colors import LIGHT_THEME

def get_light_stylesheet():
    return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {LIGHT_THEME["BACKGROUND"]};
        }}

        /* Sidebar Container */
        #Sidebar {{
            background-color: {LIGHT_THEME["CARD"]};
            border-right: 1px solid {LIGHT_THEME["BORDER"]};
        }}

        /* Sidebar Header */
        #SidebarHeader {{
            background-color: {LIGHT_THEME["SECONDARY"]};
            border-bottom: 1px solid {LIGHT_THEME["BORDER"]};
        }}

        #AppTitle {{
            background-color: transparent;
            color: {LIGHT_THEME["FOREGROUND"]};
            font-weight: bold;
        }}

        #SidebarHeader QLabel {{
            background-color: transparent;
        }}

        /* Sidebar Navigation */
        #SidebarNav {{
            background-color: transparent;
        }}

        /* Sidebar Buttons */
        #SidebarButton {{
            background-color: transparent;
            color: {LIGHT_THEME["MUTED_FOREGROUND"]};
            border: none;
            border-radius: 8px;
            text-align: left;
            padding-left: 15px;
            font-weight: 500;
        }}

        #SidebarButton:hover {{
            background-color: {LIGHT_THEME["HOVER"]};
            color: {LIGHT_THEME["ACCENT_FOREGROUND"]};
        }}

        #SidebarButton:checked {{
            background-color: {LIGHT_THEME["PRIMARY"]};
            color: {LIGHT_THEME["PRIMARY_FOREGROUND"]};
            font-weight: 600;
        }}

        #SidebarButton:checked:hover {{
            background-color: {LIGHT_THEME["RING"]};
        }}

        #SidebarButton:pressed {{
            background-color: {LIGHT_THEME["PRIMARY"]};
        }}

        /* Settings Submenu */
        #SettingsSubMenu {{
            background-color: transparent;
        }}

        /* Sidebar Footer */
        #SidebarFooter {{
            background-color: transparent;
            border-top: 1px solid {LIGHT_THEME["BORDER"]};
        }}

        #VersionLabel {{
            color: {LIGHT_THEME["MUTED_FOREGROUND"]};
            font-size: 11px;
        }}

        /* Content Area */
        QWidget {{
            background-color: {LIGHT_THEME["BACKGROUND"]};
            color: {LIGHT_THEME["TEXT"]};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {LIGHT_THEME["PRIMARY"]};
            color: {LIGHT_THEME["PRIMARY_FOREGROUND"]};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {LIGHT_THEME["RING"]};
        }}

        QPushButton:pressed {{
            background-color: {LIGHT_THEME["PRIMARY"]};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {LIGHT_THEME["BACKGROUND"]};
            color: {LIGHT_THEME["FOREGROUND"]};
            border: 1px solid {LIGHT_THEME["INPUT"]};
            border-radius: 6px;
            padding: 8px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {LIGHT_THEME["RING"]};
        }}

        /* Labels */
        QLabel {{
            color: {LIGHT_THEME["FOREGROUND"]};
        }}

        /* Navbar and Footer */
        Navbar, Footer {{
            background-color: {LIGHT_THEME["CARD"]};
            border: 1px solid {LIGHT_THEME["BORDER"]};
        }}

        /* Scrollbar */
        QScrollBar:vertical {{
            background-color: {LIGHT_THEME["CARD"]};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {LIGHT_THEME["MUTED"]};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {LIGHT_THEME["MUTED_FOREGROUND"]};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """