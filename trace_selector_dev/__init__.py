import time

starttime = time.time()
from .gui.gui import MainWindow
print("MainWindow", round(time.time()-starttime,3), "s")
from .utils.configuration import gui_settings
print("Gui Settings", round(time.time()-starttime,3), "s")
from .detection.model_zoo import ModelZoo
print("ModelZoo", round(time.time()-starttime,3), "s")

from PyQt6.QtWidgets import QApplication
import sys
from platformdirs import user_data_dir

print("Rest", round(time.time()-starttime,3), "s")

class App:
    main: MainWindow = None
    def start(): 
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
        print("Showing", round(time.time()-starttime,3), "s")
        sys.exit(app.exec())