import os

COMPONENT_STYLES = [
    "base",
    "sidebar",
    "button",
    "input",
    "navbar",
    "scrollbar",
    "table",
    "dialog"
]

def load_and_format_stylesheet(theme):
    """
    Loads all component .qss files, formats them with the given theme's colors,
    and returns a single stylesheet string.
    """
    full_stylesheet = []
    style_dir = os.path.dirname(os.path.abspath(__file__))
    components_dir = os.path.join(style_dir, "components")

    for component_name in COMPONENT_STYLES:
        file_path = os.path.join(components_dir, f"{component_name}.qss")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = f.read()
                full_stylesheet.append(template.format(**theme))
        except FileNotFoundError:
            print(f"Warning: Style file not found for component: {component_name}.qss")
        except Exception as e:
            print(f"Error processing style file {component_name}.qss: {e}")
            
    return "\n".join(full_stylesheet)
