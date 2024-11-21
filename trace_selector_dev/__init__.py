from .gui.gui import MainWindow
from .utils.configuration import gui_settings
from .detection.model_zoo import ModelZoo

from PyQt6.QtWidgets import QApplication
import sys
from platformdirs import user_data_dir

class App:
    main: MainWindow = None
    def ini(): 
        # get modelzoo directory
        modelzoo_folder = user_data_dir("trace_selector")
        # check for available ML models
        modelzoo = ModelZoo(modelzoo_folder)
        modelzoo.check_for_updates()
        # initalize settings
        settings = gui_settings(modelzoo)
        # initalize GUI
        app = QApplication(sys.argv)
        App.main = MainWindow(settings)
        App.main.show()
        sys.exit(app.exec())

    def start():
        App.ini()
 

if __name__ == "__main__":
    App.start()
