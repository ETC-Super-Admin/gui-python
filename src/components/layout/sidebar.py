import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

from .sidebar_buttons import create_nav_button, create_expandable_button, update_expandable_button_state
from .settings_submenu import SettingsSubMenu
from .admin_submenu import AdminSubMenu # New import

class Sidebar(QWidget):
    page_changed = Signal(str)
    
    def __init__(self, theme_manager, username, role):
        super().__init__()
        self.setObjectName("Sidebar")
        self.theme_manager = theme_manager
        self.settings_expanded = False
        self.admin_expanded = False # New state for admin submenu
        self.username = username
        self.role = role

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

        self.bills_process_button = create_nav_button(
            qta.icon('fa5s.file-invoice-dollar', color='#64748b'), 
            "Bills Process"
        )

        self.shipping_label_button = create_nav_button(
            qta.icon('fa5s.shipping-fast', color='#64748b'), 
            "Shipping Label"
        )

        self.help_button = create_nav_button(
            qta.icon('fa5s.question-circle', color='#64748b'), 
            "Help"
        )

        # Admin button with chevron (custom widget)
        self.admin_button, self.admin_icon_label, self.admin_chevron_label = create_expandable_button(
            'fa5s.user-shield',
            "Admin",
            self.toggle_admin_submenu, # New toggle function
            self.theme_manager
        )
        
        # Settings button with chevron (custom widget)
        self.settings_button, self.settings_icon_label, self.chevron_label = create_expandable_button(
            'fa5s.cogs',
            "Settings",
            self.toggle_settings_submenu,
            self.theme_manager
        )

        nav_layout.addWidget(self.dashboard_button)
        nav_layout.addWidget(self.analytics_button)
        nav_layout.addWidget(self.projects_button)
        nav_layout.addWidget(self.bills_process_button)
        nav_layout.addWidget(self.shipping_label_button)
        nav_layout.addWidget(self.help_button)
        nav_layout.addWidget(self.admin_button)

        # Admin submenu
        self.admin_submenu = AdminSubMenu(parent=self, create_nav_button_func=create_nav_button)
        nav_layout.addWidget(self.admin_submenu)
        self.admin_submenu.hide()

        nav_layout.addWidget(self.settings_button)

        # Settings submenu
        self.settings_submenu = SettingsSubMenu(parent=self, create_nav_button_func=create_nav_button, user_role=self.role)
        nav_layout.addWidget(self.settings_submenu)
        self.settings_submenu.hide()

        layout.addWidget(nav_widget)
        layout.addStretch()

        # Footer section
        footer = QWidget()
        footer.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 4, 20, 4)

        version_label = QLabel("v1.0.0")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)

        layout.addWidget(footer)

        self.buttons = {
            "dashboard": self.dashboard_button,
            "analytics": self.analytics_button,
            "projects": self.projects_button,
            "bills_process": self.bills_process_button,
            "shipping_label": self.shipping_label_button,
            "help": self.help_button,
            "settings": self.settings_button,
            "general_settings": self.settings_submenu.general_settings_button,
            "admin": self.admin_button,
            "user_management": self.admin_submenu.user_management_button,
            "timesheets": self.admin_submenu.timesheets_button,
        }

        # Connect signals
        self.dashboard_button.clicked.connect(lambda: self.on_button_clicked("dashboard"))
        self.analytics_button.clicked.connect(lambda: self.on_button_clicked("analytics"))
        self.projects_button.clicked.connect(lambda: self.on_button_clicked("projects"))
        self.bills_process_button.clicked.connect(lambda: self.on_button_clicked("bills_process"))
        self.shipping_label_button.clicked.connect(lambda: self.on_button_clicked("shipping_label"))
        self.help_button.clicked.connect(lambda: self.on_button_clicked("help"))

        self.admin_submenu.sub_page_changed.connect(self.on_button_clicked)

        self.settings_submenu.general_settings_button.clicked.connect(lambda: self.on_button_clicked("general_settings"))

        if self.role != 'admin':
            self.admin_button.hide()

        # Set initial active button
        self.set_active_button("dashboard")

    def update_user_info(self, username, role):
        self.username = username
        self.role = role
        if self.role == 'admin':
            self.admin_button.show()
        else:
            self.admin_button.hide()
            if self.admin_expanded:
                self.admin_submenu.hide()
                self.admin_expanded = False
                # Reset chevron icon
                chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
                self.admin_chevron_label.setPixmap(chevron_icon.pixmap(12, 12))

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

    def toggle_admin_submenu(self): # New toggle function
        current_theme = self.theme_manager.get_current_theme_colors()
        
        self.admin_expanded = not self.admin_expanded
        
        if self.admin_expanded:
            self.admin_submenu.show()
            chevron_icon = qta.icon('fa5s.chevron-up', color='#64748b')
            self.admin_chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
        else:
            self.admin_submenu.hide()
            chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
            self.admin_chevron_label.setPixmap(chevron_icon.pixmap(12, 12))

    def on_button_clicked(self, button_name):
        # Close settings submenu if clicking on non-settings button
        if button_name not in ["settings", "general_settings"]:# Removed settings_user_management
            if self.settings_expanded:
                self.settings_expanded = False
                self.settings_submenu.hide()
                chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
                self.chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
        
        # Close admin submenu if clicking on non-admin button
        if button_name not in ["admin", "user_management", "timesheets"]:
            if self.admin_expanded:
                self.admin_expanded = False
                self.admin_submenu.hide()
                chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
                self.admin_chevron_label.setPixmap(chevron_icon.pixmap(12, 12))
        
        self.set_active_button(button_name)
        self.page_changed.emit(button_name)

    def set_active_button(self, button_name):
        current_theme = self.theme_manager.get_current_theme_colors()
        
        # If access denied, clear all active buttons and do not highlight anything
        if button_name == "access_denied":
            for name, button in self.buttons.items():
                if name not in ["settings", "admin"]: # Don't uncheck settings/admin button itself, only its sub-items
                    button.setChecked(False)
                    # Reset icon color to default
                    icon_name_map = {
                        "dashboard": 'fa5s.tachometer-alt',
                        "analytics": 'fa5s.chart-line',
                        "projects": 'fa5s.folder',
                        "bills_process": 'fa5s.file-invoice-dollar',
                        "shipping_label": 'fa5s.shipping-fast',
                        "help": 'fa5s.question-circle',
                        "general_settings": 'fa5s.sliders-h',
                        "admin": 'fa5s.user-shield',
                        "user_management": 'fa5s.users',
                        "timesheets": 'fa5s.clock'
                    }
                    if name in icon_name_map:
                        button.setIcon(qta.icon(icon_name_map[name], color='#64748b'))
            update_expandable_button_state(self.settings_button, False, self.theme_manager, self.settings_icon_label, self.chevron_label, 'fa5s.cogs')
            self.settings_expanded = False
            self.settings_submenu.hide()
            update_expandable_button_state(self.admin_button, False, self.theme_manager, self.admin_icon_label, self.admin_chevron_label, 'fa5s.user-shield') # Update admin button state
            self.admin_expanded = False
            self.admin_submenu.hide()
            return

        for name, button in self.buttons.items():
            if name in ["settings", "admin"]:
                continue  # Handle settings and admin buttons separately
            
            is_active = name == button_name
            button.setChecked(is_active)
            
            # Update icon color based on active state
            icon_name_map = {
                "dashboard": 'fa5s.tachometer-alt',
                "analytics": 'fa5s.chart-line',
                "projects": 'fa5s.folder',
                "bills_process": 'fa5s.file-invoice-dollar',
                "shipping_label": 'fa5s.shipping-fast',
                "help": 'fa5s.question-circle',
                "general_settings": 'fa5s.sliders-h',
                "admin": 'fa5s.user-shield',
                "user_management": 'fa5s.users',
                "timesheets": 'fa5s.clock'
            }
            
            if name in icon_name_map:
                if is_active:
                    button.setIcon(qta.icon(icon_name_map[name], color=current_theme["PRIMARY_FOREGROUND"])) # Use PRIMARY_FOREGROUND for active
                else:
                    button.setIcon(qta.icon(icon_name_map[name], color='#64748b'))
        
        # Handle settings button highlighting
        if button_name == "general_settings":
            update_expandable_button_state(self.settings_button, True, self.theme_manager, self.settings_icon_label, self.chevron_label, 'fa5s.cogs')
            self.settings_expanded = True # Ensure submenu is open when a sub-page is active
            self.settings_submenu.show()
        else:
            update_expandable_button_state(self.settings_button, False, self.theme_manager, self.settings_icon_label, self.chevron_label, 'fa5s.cogs')
            # If a main button is clicked, ensure sub-menu is hidden
            if self.settings_submenu.isVisible():
                self.settings_submenu.hide()

        # Handle admin button highlighting
        if button_name == "user_management" or button_name == "timesheets":
            update_expandable_button_state(self.admin_button, True, self.theme_manager, self.admin_icon_label, self.admin_chevron_label, 'fa5s.user-shield')
            self.admin_expanded = True # Ensure submenu is open when a sub-page is active
            self.admin_submenu.show()
        else:
            update_expandable_button_state(self.admin_button, False, self.theme_manager, self.admin_icon_label, self.admin_chevron_label, 'fa5s.user-shield')
            # If a main button is clicked, ensure sub-menu is hidden
            if self.admin_submenu.isVisible():
                self.admin_submenu.hide()
