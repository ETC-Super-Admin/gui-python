import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from src.app.layout import MainLayout
from src.styles.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self, theme_manager):
        super().__init__()
        self.setWindowTitle("Jira Inspired App")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = MainLayout(theme_manager)
        self.setCentralWidget(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    theme_manager = ThemeManager(app)
    theme_manager.set_light_theme()

    window = MainWindow(theme_manager)
    window.show()
    sys.exit(app.exec())
