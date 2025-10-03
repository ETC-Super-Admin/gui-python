import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

from .sidebar_buttons import create_nav_button, create_expandable_button, update_expandable_button_state
from .settings_submenu import SettingsSubMenu

class Sidebar(QWidget):
    page_changed = Signal(str)
    
    def __init__(self, theme_manager):
        super().__init__()
        self.setObjectName("Sidebar")
        self.theme_manager = theme_manager
        self.settings_expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header section
        header = QWidget()
        header.setObjectName("SidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 30, 20, 30)
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.setSpacing(10)

        # App Icon
        app_icon_label = QLabel()
        app_icon_pixmap = QPixmap("public/pro-icon.ico")
        if not app_icon_pixmap.isNull():
            app_icon_label.setPixmap(app_icon_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.addWidget(app_icon_label)
        
        app_title = QLabel("Pro Auto")
        app_title.setObjectName("AppTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        app_title.setFont(title_font)
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        
        layout.addWidget(header)

        # Navigation section
        nav_widget = QWidget()
        nav_widget.setObjectName("SidebarNav")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(15, 20, 15, 20)
        nav_layout.setSpacing(8)

        # Create navigation buttons
        self.dashboard_button = create_nav_button(
            qta.icon('fa5s.tachometer-alt', color='#64748b'), 
            "Dashboard"
        )
        self.analytics_button = create_nav_button(
            qta.icon('fa5s.chart-line', color='#64748b'), 
            "Analytics"
        )
        self.projects_button = create_nav_button(
            qta.icon('fa5s.folder', color='#64748b'), 
            "Projects"
        )
        
        # Settings button with chevron (custom widget)
        self.settings_button, self.settings_icon_label, self.chevron_label = create_expandable_button(
            qta.icon('fa5s.cogs', color='#64748b'),
            "Settings",
            self.toggle_settings_submenu,
            self.theme_manager
        )

        self.profile_button = create_nav_button(
            qta.icon('fa5s.user', color='#64748b'), 
            "Profile"
        )

        nav_layout.addWidget(self.dashboard_button)
        nav_layout.addWidget(self.analytics_button)
        nav_layout.addWidget(self.projects_button)
        nav_layout.addWidget(self.settings_button)
        
        # Settings submenu
        self.settings_submenu = SettingsSubMenu(parent=self, create_nav_button_func=create_nav_button)
        nav_layout.addWidget(self.settings_submenu)
        self.settings_submenu.hide()

        nav_layout.addWidget(self.profile_button)
        
        layout.addWidget(nav_widget)
        layout.addStretch()

        # Footer section
        footer = QWidget()
        footer.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 20, 20, 20)
        
        version_label = QLabel("v1.0.0")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)
        
        layout.addWidget(footer)

        self.buttons = {
            "dashboard": self.dashboard_button,
            "analytics": self.analytics_button,
            "projects": self.projects_button,
            "settings": self.settings_button,
            "general_settings": self.settings_submenu.general_settings_button,
            "user_management": self.settings_submenu.user_management_button,
            "profile": self.profile_button,
        }

        # Connect signals
        self.dashboard_button.clicked.connect(lambda: self.on_button_clicked("dashboard"))
        self.analytics_button.clicked.connect(lambda: self.on_button_clicked("analytics"))
        self.projects_button.clicked.connect(lambda: self.on_button_clicked("projects"))
        self.profile_button.clicked.connect(lambda: self.on_button_clicked("profile"))
        
        self.settings_submenu.general_settings_button.clicked.connect(lambda: self.on_button_clicked("general_settings"))
        self.settings_submenu.user_management_button.clicked.connect(lambda: self.on_button_clicked("user_management"))

        # Set initial active button
        self.set_active_button("dashboard")

    def toggle_settings_submenu(self):
        current_theme = self.theme_manager.get_current_theme_colors()
        
        self.settings_expanded = not self.settings_expanded
        
        if self.settings_expanded:
            self.settings_submenu.show()
            chevron_icon = qta.icon('fa5s.chevron-up', color='#64748b')
            self.chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
        else:
            self.settings_submenu.hide()
            chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
            self.chevron_label.setPixmap(chevron_icon.pixmap(12, 12))

    def on_button_clicked(self, button_name):
        # Close settings submenu if clicking on non-settings button
        if button_name not in ["settings", "general_settings", "user_management"]:
            if self.settings_expanded:
                self.settings_expanded = False
                self.settings_submenu.hide()
                chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
                self.chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
        
        self.set_active_button(button_name)
        self.page_changed.emit(button_name)

    def set_active_button(self, button_name):
        current_theme = self.theme_manager.get_current_theme_colors()
        
        for name, button in self.buttons.items():
            if name == "settings":
                continue  # Handle settings button separately
                
            is_active = name == button_name
            button.setChecked(is_active)
            
            # Update icon color based on active state
            icon_name_map = {
                "dashboard": 'fa5s.tachometer-alt',
                "analytics": 'fa5s.chart-line',
                "projects": 'fa5s.folder',
                "general_settings": 'fa5s.sliders-h',
                "user_management": 'fa5s.users',
                "profile": 'fa5s.user'
            }
            
            if name in icon_name_map:
                if is_active:
                    button.setIcon(qta.icon(icon_name_map[name], color=current_theme["PRIMARY_FOREGROUND"]))
                else:
                    button.setIcon(qta.icon(icon_name_map[name], color='#64748b'))
        
        # Handle settings button highlighting
        if button_name in ["general_settings", "user_management"]:
            update_expandable_button_state(self.settings_button, True, self.theme_manager, self.settings_icon_label, self.chevron_label)
            self.settings_expanded = True # Ensure submenu is open when a sub-page is active
            self.settings_submenu.show()
        else:
            update_expandable_button_state(self.settings_button, False, self.theme_manager, self.settings_icon_label, self.chevron_label)
            # If a main button is clicked, ensure sub-menu is hidden
            if self.settings_submenu.isVisible():
                self.settings_submenu.hide()
