from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                               QVBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QFont
import qtawesome as qta

class AvatarButton(QPushButton):
    """Custom avatar button with initials and green online indicator"""
    def __init__(self, initials="JD", size=36, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.size = size
        self.bg_color = QColor("#3b82f6")
        self.bg_hover_color = QColor("#2563eb")
        self.outline_color = QColor("#10b981")
        self.is_hovered = False
        
        self.setFixedSize(size + 4, size + 4)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw green outline circle (2px thick)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.outline_color)
        painter.drawEllipse(0, 0, self.size + 4, self.size + 4)
        
        # Draw circle background (inner circle) with hover effect
        bg = self.bg_hover_color if self.is_hovered else self.bg_color
        painter.setBrush(bg)
        painter.drawEllipse(2, 2, self.size, self.size)
        
        # Draw initials
        painter.setPen(QColor("#ffffff"))
        font = QFont()
        font.setPixelSize(int(self.size * 0.4))
        font.setBold(True)
        font.setFamily("Segoe UI, Arial, sans-serif")
        painter.setFont(font)
        painter.drawText(2, 2, self.size, self.size, Qt.AlignCenter, self.initials)

class DropdownMenu(QFrame):
    """Modern dropdown menu for user actions"""
    logout_clicked = Signal()
    profile_clicked = Signal()
    settings_clicked = Signal()
    switch_account_clicked = Signal() # New signal
    
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.setObjectName("DropdownMenu")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        self.setup_ui(user_info)
        
    def setup_ui(self, user_info):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # User info section
        user_info_widget = QWidget()
        user_info_widget.setObjectName("UserInfo")
        user_layout = QVBoxLayout(user_info_widget)
        user_layout.setContentsMargins(12, 8, 12, 8)
        
        name_label = QLabel(user_info.get("name", ""))
        name_label.setObjectName("UserName")
        email_label = QLabel(user_info.get("email", ""))
        email_label.setObjectName("UserEmail")
        
        user_layout.addWidget(name_label)
        user_layout.addWidget(email_label)
        layout.addWidget(user_info_widget)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("MenuSeparator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Menu items
        self.profile_btn = self.create_menu_item("fa5s.user", "Profile")
        self.profile_btn.clicked.connect(self.profile_clicked)
        layout.addWidget(self.profile_btn)
        
        self.settings_btn = self.create_menu_item("fa5s.cog", "Settings")
        self.settings_btn.clicked.connect(self.settings_clicked)
        layout.addWidget(self.settings_btn)

        self.switch_account_btn = self.create_menu_item("fa5s.exchange-alt", "Switch Account")
        self.switch_account_btn.clicked.connect(self.switch_account_clicked)
        layout.addWidget(self.switch_account_btn)
        
        # Another separator
        separator2 = QFrame()
        separator2.setObjectName("MenuSeparator")
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFixedHeight(1)
        layout.addWidget(separator2)
        
        # Logout button
        self.logout_btn = self.create_menu_item("fa5s.sign-out-alt", "Logout", danger=True)
        self.logout_btn.clicked.connect(self.logout_clicked)
        layout.addWidget(self.logout_btn)
        
    def create_menu_item(self, icon_name, text, danger=False):
        btn = QPushButton(qta.icon(icon_name, color='#6b7280'), f"  {text}")
        btn.setObjectName("DangerMenuItem" if danger else "MenuItem")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        return btn

class Navbar(QWidget):
    sidebar_toggled = Signal()
    logout_requested = Signal()
    profile_requested = Signal()
    settings_requested = Signal()
    switch_account_requested = Signal() # New signal

    def __init__(self, theme_manager, username, role):
        super().__init__()
        self.setObjectName("Navbar")
        self.theme_manager = theme_manager
        self.is_dark_theme = False
        self.dropdown_menu = None
        self.dropdown_visible = False
        self.user_info = {"name": username, "email": "", "initials": username[0].upper() if username else ""}
        self.username = username
        self.role = role
        
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        # Left section - Sidebar toggle
        self.sidebar_toggle_button = QPushButton("")
        self.sidebar_toggle_button.setObjectName("NavbarIconButton")
        self.sidebar_toggle_button.setFixedSize(40, 40)
        self.sidebar_toggle_button.setCursor(Qt.PointingHandCursor)
        self.sidebar_toggle_button.clicked.connect(self.sidebar_toggled)
        layout.addWidget(self.sidebar_toggle_button)
        self.update_sidebar_toggle_icon(True)

        # Spacer
        layout.addStretch()

        # Right section - Theme toggle and Avatar
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Theme toggle button
        self.theme_button = QPushButton(qta.icon('fa5s.moon', color='#6b7280'), "")
        self.theme_button.setObjectName("NavbarIconButton")
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.toggle_theme)
        right_layout.addWidget(self.theme_button)

        # Avatar button
        self.avatar = AvatarButton("JD", 36)
        self.avatar.clicked.connect(self.toggle_dropdown_menu)
        right_layout.addWidget(self.avatar)
        
        layout.addWidget(right_section)

    def toggle_theme(self):
        if self.is_dark_theme:
            self.theme_manager.set_light_theme()
            self.theme_button.setIcon(qta.icon('fa5s.moon', color='#6b7280'))
        else:
            self.theme_manager.set_dark_theme()
            self.theme_button.setIcon(qta.icon('fa5s.sun', color='#fbbf24'))
        self.is_dark_theme = not self.is_dark_theme

    def update_sidebar_toggle_icon(self, is_expanded):
        color = '#fbbf24' if self.is_dark_theme else '#6b7280'
        if is_expanded:
            self.sidebar_toggle_button.setIcon(qta.icon('fa5s.arrow-left', color=color))
        else:
            self.sidebar_toggle_button.setIcon(qta.icon('fa5s.bars', color=color))
    
    def toggle_dropdown_menu(self):
        """Toggle dropdown menu visibility"""
        if self.dropdown_visible and self.dropdown_menu:
            self.dropdown_menu.hide()
            self.dropdown_visible = False
        else:
            self.show_dropdown_menu()
    
    def show_dropdown_menu(self):
        """Show the dropdown menu"""
        if self.dropdown_menu is None:
            self.dropdown_menu = DropdownMenu(self.user_info, None)
            self.dropdown_menu.logout_clicked.connect(self.on_logout_clicked)
            self.dropdown_menu.profile_clicked.connect(self.on_profile_clicked)
            self.dropdown_menu.settings_clicked.connect(self.on_settings_clicked)
            self.dropdown_menu.switch_account_clicked.connect(self.on_switch_account_clicked)
        
        # Position dropdown below avatar
        pos = self.avatar.mapToGlobal(QPoint(0, 0))
        menu_width = 240
        self.dropdown_menu.setFixedWidth(menu_width)
        self.dropdown_menu.move(
            pos.x() + self.avatar.width() - menu_width,
            pos.y() + self.avatar.height() + 8
        )
        self.dropdown_menu.show()
        self.dropdown_menu.raise_()
        self.dropdown_visible = True
    
    def on_logout_clicked(self):
        """Handle logout click"""
        if self.dropdown_menu:
            self.dropdown_menu.hide()
            self.dropdown_visible = False
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Logout', "Are you sure you want to log out?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
    
    def on_profile_clicked(self):
        """Handle profile click"""
        if self.dropdown_menu:
            self.dropdown_menu.hide()
            self.dropdown_visible = False
        self.profile_requested.emit()
    
    def on_settings_clicked(self):
        """Handle settings click"""
        if self.dropdown_menu:
            self.dropdown_menu.hide()
            self.dropdown_visible = False
        self.settings_requested.emit()

    def on_switch_account_clicked(self):
        """Handle switch account click"""
        if self.dropdown_menu:
            self.dropdown_menu.hide()
            self.dropdown_visible = False
        self.switch_account_requested.emit()
    
    def set_user_info(self, name, email, initials=None):
        """Update user information displayed in navbar and dropdown"""
        self.user_info["name"] = name
        self.user_info["email"] = email
        if initials is not None:
            self.user_info["initials"] = initials
            self.avatar.initials = initials
            self.avatar.update()
        
        # Invalidate the dropdown to recreate it with new info
        self.dropdown_menu = None