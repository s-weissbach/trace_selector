from gui import ui_window
from configuration import gui_settings
from PyQt6.QtWidgets import QApplication
import sys

def main():
    settings = gui_settings()
    app = QApplication(sys.argv)
    main = ui_window(settings)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

