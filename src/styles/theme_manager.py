from PySide6.QtWidgets import QApplication
from src.styles.light_theme import get_light_stylesheet
from src.styles.dark_theme import get_dark_stylesheet
from src.styles.colors import LIGHT_THEME, DARK_THEME

class ThemeManager:
    _instance = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if app is not None:
                cls._instance._init_once(app)
        return cls._instance

    def _init_once(self, app):
        self.app = app
        self.light_theme_stylesheet = get_light_stylesheet()
        self.dark_theme_stylesheet = get_dark_stylesheet()
        self.current_theme_name = "light" # Default theme

    def __init__(self, app=None):
        # __init__ might be called multiple times for a singleton, but _init_once ensures setup only happens once
        pass

    @staticmethod
    def get_instance(app=None):
        if ThemeManager._instance is None:
            if app is None:
                raise RuntimeError("ThemeManager must be initialized with a QApplication instance first.")
            ThemeManager(app) # Initialize the singleton
        return ThemeManager._instance

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