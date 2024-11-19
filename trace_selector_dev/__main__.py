from .gui.gui import MainWindow
from .utils.configuration import gui_settings
from .detection.model_zoo import ModelZoo

from PyQt6.QtWidgets import QApplication
import sys
from platformdirs import user_data_dir
import threading

class App:
    main: MainWindow = None
    stdinThread: threading.Thread = None
    def ini():
        App.stdinThread = threading.Thread(target=App.readStdIn)
        App.stdinThread.start()  
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

    def readStdIn():
        print("Ich werde gestartet")
        i = 0
        while (line := sys.stdin.read()) != b"":
            print(i, line)
            i += 1
            sys.stdout.flush()
        print("Ich bin fertig")

 


class API:
    def OpenFile(data: str):
        App.main.synapse_response.open_file(
            data,
            ".virtual",
            App.main.get_setting("meta_columns"),
            App.main.get_setting("normalization_use_median"),
            App.main.get_setting("normalization_sliding_window_size"),
        )
        App.main.labels = []

        App.main.switch_to_main_layout()
        App.main.plot()
        App.main.current_roi_label.setText(
            f"Current ROI: {App.main.synapse_response.columns[App.main.synapse_response.idx]}"
        )

if __name__ == "__main__":
    App.start()
