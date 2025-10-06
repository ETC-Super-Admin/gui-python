from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy, QApplication
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal
from src.components.layout.navbar import Navbar
from src.components.layout.sidebar import Sidebar
from src.app.dashboard.dashboard import Dashboard
from src.app.analytics.analytics import Analytics
from src.app.projects.projects import Projects
from src.app.settings.general_settings import GeneralSettings
from src.app.admin.user_management import UserManagement
from src.app.settings.settings import Settings
from src.app.profile.profile import Profile
from src.app.help.help import Help
from src.app.bills_process.bills_process import BillsProcess
from src.app.bills_process.cell_config import CellConfig
from src.app.bills_process.path_config import PathConfig
from src.app.shipping_label.shipping_label import ShippingLabel

from src.app.shipping_label.label_asset import LabelAsset
from src.app.shipping_label.sender_management import SenderManagement
from src.app.shipping_label.receiver_management import ReceiverManagement
from src.app.shipping_label.delivery_management import DeliveryManagement
from src.app.admin.admin import Admin
from src.app.admin.timesheets import Timesheets
from src.app.access_denied import AccessDenied
from src.user_manager import UserManager

class MainLayout(QWidget):
    reauthenticate_requested = Signal()

    def __init__(self, theme_manager, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.user_manager = UserManager()

        self.permission_matrix = {
            "admin": ["dashboard", "analytics", "projects", "settings", "general_settings", "user_management", "profile", "help", "bills_process", "cell_config", "path_config", "shipping_label", "label_asset", "sender_management", "receiver_management", "delivery_management", "admin", "timesheets"],
            "user": ["dashboard", "analytics", "projects", "settings", "general_settings", "profile", "help", "bills_process", "cell_config", "path_config", "shipping_label", "label_asset", "sender_management", "receiver_management", "delivery_management"],
        }

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar(theme_manager, username, role)
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(300)
        self.sidebar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_layout.addWidget(self.sidebar, 1)

        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(250)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuart)

        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_area, 4)

        self.navbar = Navbar(theme_manager, username, role)
        initials = username[0].upper() if username else ""
        self.navbar.set_user_info(username, "john.doe@example.com", initials)
        content_layout.addWidget(self.navbar)

        self.page_container = QStackedWidget()
        content_layout.addWidget(self.page_container)

        self.pages = {
            "dashboard": Dashboard(),
            "analytics": Analytics(),
            "projects": Projects(),
            "settings": Settings(),
            "general_settings": GeneralSettings(),
            "user_management": UserManagement(),
            "profile": Profile(),
            "help": Help(),
            "bills_process": BillsProcess(),
            "cell_config": CellConfig(),
            "path_config": PathConfig(),
            "shipping_label": ShippingLabel(),

            "label_asset": LabelAsset(),
            "sender_management": SenderManagement(),
            "receiver_management": ReceiverManagement(),
            "delivery_management": DeliveryManagement(),
            "admin": Admin(),
            "timesheets": Timesheets(),
            "access_denied": AccessDenied(),
        }

        for page in self.pages.values():
            self.page_container.addWidget(page)

        self.sidebar.page_changed.connect(self.switch_page)
        self.navbar.sidebar_toggled.connect(self.toggle_sidebar)
        self.navbar.profile_requested.connect(lambda: self.switch_page("profile"))
        self.navbar.settings_requested.connect(lambda: self.switch_page("settings"))

        last_active_page = self.user_manager.get_last_active_page()
        self.switch_page(last_active_page)

    def update_user_info(self, username, role):
        self.username = username
        self.role = role
        initials = username[0].upper() if username else ""
        self.navbar.set_user_info(username, "john.doe@example.com", initials)
        self.sidebar.update_user_info(username, role)

        destination = self.user_manager.intended_destination or self.user_manager.get_last_active_page()
        self.switch_page(destination)
        self.user_manager.intended_destination = None

    def toggle_sidebar(self):
        is_expanded = self.sidebar.maximumWidth() == 300
        if is_expanded:
            self.sidebar_animation.setStartValue(300)
            self.sidebar_animation.setEndValue(0)
        else:
            self.sidebar_animation.setStartValue(0)
            self.sidebar_animation.setEndValue(300)
        self.sidebar_animation.start()
        self.navbar.update_sidebar_toggle_icon(not is_expanded)

    def switch_page(self, page_name):
        if page_name not in self.pages:
            print(f"Page '{page_name}' not found, defaulting to dashboard.")
            page_name = "dashboard"

        has_permission = self.role in self.permission_matrix and page_name in self.permission_matrix.get(self.role, [])

        if has_permission:
            self.page_container.setCurrentWidget(self.pages[page_name])
            self.sidebar.set_active_button(page_name)
            self.user_manager.save_last_active_page(page_name)
        else:
            if self.user_manager.is_logged_in():
                self.page_container.setCurrentWidget(self.pages["dashboard"])
                self.sidebar.set_active_button("dashboard")
                self.user_manager.save_last_active_page("dashboard")
            else:
                self.user_manager.intended_destination = page_name
                self.reauthenticate_requested.emit()
                self.page_container.setCurrentWidget(self.pages["dashboard"])
                self.sidebar.set_active_button("dashboard")
