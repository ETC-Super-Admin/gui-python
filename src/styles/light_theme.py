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

        /* Navbar */
        #Navbar {{
            background-color: {LIGHT_THEME["CARD"]};
            border-bottom: 1px solid {LIGHT_THEME["BORDER"]};
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
            background-color: {LIGHT_THEME["HOVER"]};
        }}

        #NavbarIconButton:pressed {{
            background-color: {LIGHT_THEME["SECONDARY"]};
        }}

        /* Avatar Container */
        #AvatarContainer {{
            background-color: transparent;
            border: none;
            border-radius: 22px;
            padding: 4px;
        }}

        #AvatarContainer:hover {{
            background-color: rgba(59, 130, 246, 0.1);
        }}

        /* Override button styles for avatar area */
        #AvatarContainer QPushButton {{
            background-color: transparent;
            border: none;
            padding: 0px;
        }}

        /* Dropdown Menu */
        #DropdownMenu {{
            background-color: {LIGHT_THEME["CARD"]};
            border: 1px solid {LIGHT_THEME["BORDER"]};
            border-radius: 12px;
            min-width: 220px;
        }}

        /* User Info in Dropdown */
        #UserInfo {{
            background-color: transparent;
        }}

        #UserName {{
            color: {LIGHT_THEME["FOREGROUND"]};
            font-weight: 600;
            font-size: 14px;
        }}

        #UserEmail {{
            color: {LIGHT_THEME["MUTED_FOREGROUND"]};
            font-size: 12px;
        }}

        /* Menu Separator */
        #MenuSeparator {{
            background-color: {LIGHT_THEME["BORDER"]};
            border: none;
        }}

        /* Menu Items */
        #MenuItem {{
            background-color: transparent;
            color: {LIGHT_THEME["FOREGROUND"]};
            border: none;
            border-radius: 6px;
            text-align: left;
            padding: 8px 12px;
            font-size: 14px;
        }}

        #MenuItem:hover {{
            background-color: {LIGHT_THEME["HOVER"]};
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