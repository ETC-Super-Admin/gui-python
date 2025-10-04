import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

from .sidebar_buttons import create_nav_button, create_expandable_button, update_expandable_button_state
from .settings_submenu import SettingsSubMenu
from .admin_submenu import AdminSubMenu
from .bills_process_submenu import BillsProcessSubMenu
from .shipping_label_submenu import ShippingLabelSubMenu

class Sidebar(QWidget):
    page_changed = Signal(str)
    
    def __init__(self, theme_manager, username, role):
        super().__init__()
        self.setObjectName("Sidebar")
        self.theme_manager = theme_manager
        self.settings_expanded = False
        self.admin_expanded = False
        self.bills_process_expanded = False
        self.shipping_label_expanded = False
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

        self.help_button = create_nav_button(
            qta.icon('fa5s.question-circle', color='#64748b'), 
            "Help"
        )

        # Bills Process button with chevron
        self.bills_process_button, self.bills_process_icon_label, self.bills_process_chevron_label = create_expandable_button(
            'fa5s.file-invoice-dollar',
            "Bills Process",
            self.toggle_bills_process_submenu,
            self.theme_manager
        )

        # Shipping Label button with chevron
        self.shipping_label_button, self.shipping_label_icon_label, self.shipping_label_chevron_label = create_expandable_button(
            'fa5s.shipping-fast',
            "Shipping Label",
            self.toggle_shipping_label_submenu,
            self.theme_manager
        )

        # Admin button with chevron
        self.admin_button, self.admin_icon_label, self.admin_chevron_label = create_expandable_button(
            'fa5s.user-shield',
            "Admin",
            self.toggle_admin_submenu,
            self.theme_manager
        )
        
        # Settings button with chevron
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

        # Bills Process submenu
        self.bills_process_submenu = BillsProcessSubMenu(parent=self, create_nav_button_func=create_nav_button)
        nav_layout.addWidget(self.bills_process_submenu)
        self.bills_process_submenu.hide()

        nav_layout.addWidget(self.shipping_label_button)

        # Shipping Label submenu
        self.shipping_label_submenu = ShippingLabelSubMenu(parent=self, create_nav_button_func=create_nav_button)
        nav_layout.addWidget(self.shipping_label_submenu)
        self.shipping_label_submenu.hide()

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
            "bills_process": self.bills_process_submenu.overview_button,
            "cell_config": self.bills_process_submenu.cell_config_button,
            "path_config": self.bills_process_submenu.path_config_button,
            "shipping_label": self.shipping_label_submenu.overview_button,
            "live_view": self.shipping_label_submenu.live_view_button,
            "label_asset": self.shipping_label_submenu.label_asset_button,
            "sender_management": self.shipping_label_submenu.sender_management_button,
            "receiver_management": self.shipping_label_submenu.receiver_management_button,
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
        self.help_button.clicked.connect(lambda: self.on_button_clicked("help"))

        self.bills_process_submenu.sub_page_changed.connect(self.on_button_clicked)
        self.shipping_label_submenu.sub_page_changed.connect(self.on_button_clicked)
        self.admin_submenu.sub_page_changed.connect(self.on_button_clicked)
        self.settings_submenu.sub_page_changed.connect(self.on_button_clicked)

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
                chevron_icon = qta.icon('fa5s.chevron-down', color='#64748b')
                self.admin_chevron_label.setPixmap(chevron_icon.pixmap(12, 12))

    def toggle_settings_submenu(self):
        self.settings_expanded = not self.settings_expanded
        if self.settings_expanded:
            self.settings_submenu.show()
        else:
            self.settings_submenu.hide()

    def toggle_admin_submenu(self):
        self.admin_expanded = not self.admin_expanded
        if self.admin_expanded:
            self.admin_submenu.show()
        else:
            self.admin_submenu.hide()

    def toggle_bills_process_submenu(self):
        self.bills_process_expanded = not self.bills_process_expanded
        if self.bills_process_expanded:
            self.bills_process_submenu.show()
        else:
            self.bills_process_submenu.hide()

    def toggle_shipping_label_submenu(self):
        self.shipping_label_expanded = not self.shipping_label_expanded
        if self.shipping_label_expanded:
            self.shipping_label_submenu.show()
        else:
            self.shipping_label_submenu.hide()

    def on_button_clicked(self, button_name):
        # Collapse other submenus
        if button_name not in ["settings", "general_settings"] and self.settings_expanded:
            self.toggle_settings_submenu()
        
        if button_name not in ["admin", "user_management", "timesheets"] and self.admin_expanded:
            self.toggle_admin_submenu()

        if button_name not in ["bills_process", "cell_config", "path_config"] and self.bills_process_expanded:
            self.toggle_bills_process_submenu()

        if button_name not in ["shipping_label", "live_view", "label_asset", "sender_management", "receiver_management"] and self.shipping_label_expanded:
            self.toggle_shipping_label_submenu()

        # If a main expandable button is clicked, just toggle it
        if button_name in ["settings", "admin"]:
            if button_name == "settings": self.toggle_settings_submenu()
            if button_name == "admin": self.toggle_admin_submenu()
            return

        self.set_active_button(button_name)
        self.page_changed.emit(button_name)

    def set_active_button(self, button_name):
        current_theme = self.theme_manager.get_current_theme_colors()
        
        if button_name == "access_denied":
            for name, button in self.buttons.items():
                if name not in ["settings", "admin", "bills_process", "shipping_label"]:
                    button.setChecked(False)
            # Reset all expandable buttons
            update_expandable_button_state(self.settings_button, False, self.theme_manager, self.settings_icon_label, self.chevron_label, 'fa5s.cogs')
            self.settings_expanded = False
            self.settings_submenu.hide()
            update_expandable_button_state(self.admin_button, False, self.theme_manager, self.admin_icon_label, self.admin_chevron_label, 'fa5s.user-shield')
            self.admin_expanded = False
            self.admin_submenu.hide()
            update_expandable_button_state(self.bills_process_button, False, self.theme_manager, self.bills_process_icon_label, self.bills_process_chevron_label, 'fa5s.file-invoice-dollar')
            self.bills_process_expanded = False
            self.bills_process_submenu.hide()
            update_expandable_button_state(self.shipping_label_button, False, self.theme_manager, self.shipping_label_icon_label, self.shipping_label_chevron_label, 'fa5s.shipping-fast')
            self.shipping_label_expanded = False
            self.shipping_label_submenu.hide()
            return

        for name, button in self.buttons.items():
            if name in ["settings", "admin"]:
                continue
            
            is_active = name == button_name
            button.setChecked(is_active)
            
            icon_name_map = {
                "dashboard": 'fa5s.tachometer-alt', "analytics": 'fa5s.chart-line', "projects": 'fa5s.folder',
                "help": 'fa5s.question-circle',
                "general_settings": 'fa5s.sliders-h', "user_management": 'fa5s.users', "timesheets": 'fa5s.clock',
                "bills_process": 'fa5s.file-alt', "cell_config": 'fa5s.th', "path_config": 'fa5s.folder-open',
                "shipping_label": 'fa5s.barcode', "live_view": 'fa5s.street-view', "label_asset": 'fa5s.box', "sender_management": 'fa5s.user-check', "receiver_management": 'fa5s.user-tag'
            }
            
            if name in icon_name_map:
                color = current_theme["PRIMARY_FOREGROUND"] if is_active else '#64748b'
                button.setIcon(qta.icon(icon_name_map[name], color=color))
        
        # Handle expandable buttons highlighting
        is_settings_active = button_name in ["general_settings"]
        update_expandable_button_state(self.settings_button, is_settings_active, self.theme_manager, self.settings_icon_label, self.chevron_label, 'fa5s.cogs')
        if is_settings_active and not self.settings_expanded: self.toggle_settings_submenu()

        is_admin_active = button_name in ["user_management", "timesheets"]
        update_expandable_button_state(self.admin_button, is_admin_active, self.theme_manager, self.admin_icon_label, self.admin_chevron_label, 'fa5s.user-shield')
        if is_admin_active and not self.admin_expanded: self.toggle_admin_submenu()

        is_bills_active = button_name in ["bills_process", "cell_config", "path_config"]
        update_expandable_button_state(self.bills_process_button, is_bills_active, self.theme_manager, self.bills_process_icon_label, self.bills_process_chevron_label, 'fa5s.file-invoice-dollar')
        if is_bills_active and not self.bills_process_expanded: self.toggle_bills_process_submenu()

        is_shipping_active = button_name in ["shipping_label", "live_view", "label_asset", "sender_management", "receiver_management"]
        update_expandable_button_state(self.shipping_label_button, is_shipping_active, self.theme_manager, self.shipping_label_icon_label, self.shipping_label_chevron_label, 'fa5s.shipping-fast')
        if is_shipping_active and not self.shipping_label_expanded: self.toggle_shipping_label_submenu()
