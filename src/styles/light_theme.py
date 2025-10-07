from .colors import LIGHT_THEME
from .style_loader import load_and_format_stylesheet

def get_light_stylesheet():
    return load_and_format_stylesheet(LIGHT_THEME)
