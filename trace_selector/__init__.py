__version__ = "1.0.1"

from .gui.gui import MainWindow
from .utils.configuration import gui_settings
from .detection.model_zoo import ModelZoo

from PyQt6.QtWidgets import QApplication
import sys
from platformdirs import user_data_dir

class App:
    main: MainWindow = None
    def start(): 
        # get modelzoo directory
        modelzoo_folder = user_data_dir(appname="trace_selector", appauthor=None, roaming=False)

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