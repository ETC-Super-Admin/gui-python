
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from src.components.layout.navbar import Navbar
from src.components.layout.sidebar import Sidebar
from src.components.layout.footer import Footer
from src.app.dashboard.dashboard import Dashboard
from src.app.settings.settings import Settings
from src.app.profile.profile import Profile
from src.app.analytics.analytics import Analytics
from src.app.projects.projects import Projects
from src.app.settings.general_settings import GeneralSettings
from src.app.settings.user_management import UserManagement

class MainLayout(QWidget):
    def __init__(self, theme_manager):
        super().__init__()

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(theme_manager)
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setMaximumWidth(300) # Initial width
        self.sidebar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_layout.addWidget(self.sidebar, 1)

        # Sidebar animation
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(250)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuart)

        # Content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_area, 4)

        # Navbar
        self.navbar = Navbar(theme_manager)
        content_layout.addWidget(self.navbar)

        # Page container
        self.page_container = QStackedWidget()
        content_layout.addWidget(self.page_container)

        # Add pages
        self.dashboard_page = Dashboard()
        self.analytics_page = Analytics()
        self.projects_page = Projects()
        self.settings_page = Settings()
        self.general_settings_page = GeneralSettings()
        self.user_management_page = UserManagement()
        self.profile_page = Profile()
        self.page_container.addWidget(self.dashboard_page)
        self.page_container.addWidget(self.analytics_page)
        self.page_container.addWidget(self.projects_page)
        self.page_container.addWidget(self.settings_page)
        self.page_container.addWidget(self.general_settings_page)
        self.page_container.addWidget(self.user_management_page)
        self.page_container.addWidget(self.profile_page)

        # Footer
        self.footer = Footer()
        content_layout.addWidget(self.footer)

        # Connect sidebar signals to page switching
        self.sidebar.page_changed.connect(self.switch_page)

        self.navbar.sidebar_toggled.connect(self.toggle_sidebar)

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
        if page_name == "dashboard":
            self.page_container.setCurrentWidget(self.dashboard_page)
        elif page_name == "analytics":
            self.page_container.setCurrentWidget(self.analytics_page)
        elif page_name == "projects":
            self.page_container.setCurrentWidget(self.projects_page)
        elif page_name == "settings":
            self.page_container.setCurrentWidget(self.settings_page)
        elif page_name == "general_settings":
            self.page_container.setCurrentWidget(self.general_settings_page)
        elif page_name == "user_management":
            self.page_container.setCurrentWidget(self.user_management_page)
        elif page_name == "profile":
            self.page_container.setCurrentWidget(self.profile_page)
