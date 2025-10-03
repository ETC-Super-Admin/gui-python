from src.styles.colors import DARK_THEME

def get_dark_stylesheet():
    return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {DARK_THEME["BACKGROUND"]};
        }}

        /* Sidebar Container */
        #Sidebar {{
            background-color: {DARK_THEME["CARD"]};
            border-right: 1px solid {DARK_THEME["BORDER"]};
        }}

        /* Sidebar Header */
        #SidebarHeader {{
            background-color: {DARK_THEME["SECONDARY"]};
            border-bottom: 1px solid {DARK_THEME["BORDER"]};
        }}

        #AppTitle {{
            background-color: transparent;
            color: {DARK_THEME["FOREGROUND"]};
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
            color: {DARK_THEME["MUTED_FOREGROUND"]};
            border: none;
            border-radius: 8px;
            text-align: left;
            padding-left: 15px;
            font-weight: 500;
        }}

        #SidebarButton:hover {{
            background-color: {DARK_THEME["HOVER"]};
            color: {DARK_THEME["ACCENT_FOREGROUND"]};
        }}

        #SidebarButton:checked {{
            background-color: {DARK_THEME["PRIMARY"]};
            color: {DARK_THEME["PRIMARY_FOREGROUND"]};
            font-weight: 600;
        }}

        #SidebarButton:checked:hover {{
            background-color: {DARK_THEME["RING"]};
        }}

        #SidebarButton:pressed {{
            background-color: {DARK_THEME["PRIMARY"]};
        }}

        /* Settings Submenu */
        #SettingsSubMenu {{
            background-color: transparent;
        }}

        /* Sidebar Footer */
        #SidebarFooter {{
            background-color: transparent;
            border-top: 1px solid {DARK_THEME["BORDER"]};
        }}

        #VersionLabel {{
            color: {DARK_THEME["MUTED_FOREGROUND"]};
            font-size: 11px;
        }}

        /* Content Area */
        QWidget {{
            background-color: {DARK_THEME["BACKGROUND"]};
            color: {DARK_THEME["TEXT"]};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {DARK_THEME["PRIMARY"]};
            color: {DARK_THEME["PRIMARY_FOREGROUND"]};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {DARK_THEME["RING"]};
        }}

        QPushButton:pressed {{
            background-color: {DARK_THEME["PRIMARY"]};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {DARK_THEME["CARD"]};
            color: {DARK_THEME["FOREGROUND"]};
            border: 1px solid {DARK_THEME["INPUT"]};
            border-radius: 6px;
            padding: 8px;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {DARK_THEME["RING"]};
        }}

        /* Labels */
        QLabel {{
            color: {DARK_THEME["FOREGROUND"]};
        }}

        /* Navbar */
        #Navbar {{
            background-color: {DARK_THEME["CARD"]};
            border-bottom: 1px solid {DARK_THEME["BORDER"]};
            min-height: 64px;
            max-height: 64px;
        }}

        /* Navbar Icon Buttons */
        #NavbarIconButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
            padding: 8px;
        }}

        #NavbarIconButton:hover {{
            background-color: {DARK_THEME["HOVER"]};
        }}

        #NavbarIconButton:pressed {{
            background-color: {DARK_THEME["SECONDARY"]};
        }}

        /* Dropdown Menu */
        #DropdownMenu {{
            background-color: {DARK_THEME["CARD"]};
            border: 1px solid {DARK_THEME["BORDER"]};
            border-radius: 12px;
            min-width: 220px;
        }}

        /* User Info in Dropdown */
        #UserInfo {{
            background-color: transparent;
        }}

        #UserName {{
            color: {DARK_THEME["FOREGROUND"]};
            font-weight: 600;
            font-size: 14px;
        }}

        #UserEmail {{
            color: {DARK_THEME["MUTED_FOREGROUND"]};
            font-size: 12px;
        }}

        /* Menu Separator */
        #MenuSeparator {{
            background-color: {DARK_THEME["BORDER"]};
            border: none;
        }}

        /* Menu Items */
        #MenuItem {{
            background-color: transparent;
            color: {DARK_THEME["FOREGROUND"]};
            border: none;
            border-radius: 6px;
            text-align: left;
            padding: 8px 12px;
            font-size: 14px;
        }}

        #MenuItem:hover {{
            background-color: {DARK_THEME["HOVER"]};
        }}

        #DangerMenuItem {{
            background-color: transparent;
            color: #ef4444;
            border: none;
            border-radius: 6px;
            text-align: left;
            padding: 8px 12px;
            font-size: 14px;
        }}

        #DangerMenuItem:hover {{
            background-color: rgba(239, 68, 68, 0.1);
        }}

        /* Footer */
        Footer {{
            background-color: {DARK_THEME["CARD"]};
            border: 1px solid {DARK_THEME["BORDER"]};
        }}

        /* Scrollbar */
        QScrollBar:vertical {{
            background-color: {DARK_THEME["CARD"]};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {DARK_THEME["MUTED"]};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {DARK_THEME["MUTED_FOREGROUND"]};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """