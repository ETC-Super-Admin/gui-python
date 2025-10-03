from PySide6.QtWidgets import QApplication
from src.styles.light_theme import get_light_stylesheet
from src.styles.dark_theme import get_dark_stylesheet
from src.styles.colors import LIGHT_THEME, DARK_THEME

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.light_theme_stylesheet = get_light_stylesheet()
        self.dark_theme_stylesheet = get_dark_stylesheet()
        self.current_theme_name = "light" # Default theme

    def set_light_theme(self):
        self.app.setStyleSheet(self.light_theme_stylesheet)
        self.current_theme_name = "light"

    def set_dark_theme(self):
        self.app.setStyleSheet(self.dark_theme_stylesheet)
        self.current_theme_name = "dark"

    def get_current_theme_colors(self):
        if self.current_theme_name == "light":
            return LIGHT_THEME
        else:
            return DARK_THEME