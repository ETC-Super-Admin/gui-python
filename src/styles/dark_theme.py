from .colors import DARK_THEME
from .style_loader import load_and_format_stylesheet

def get_dark_stylesheet():
    return load_and_format_stylesheet(DARK_THEME)
