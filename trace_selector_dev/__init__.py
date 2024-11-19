from .gui.gui import MainWindow
from .utils.configuration import gui_settings
from .detection.model_zoo import ModelZoo

from PyQt6.QtWidgets import QApplication
import sys
from platformdirs import user_data_dir
import threading
import pathlib
import time

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
        time.sleep(20)
        API.OpenFile(r"C:\Users\abril\Andreas Eigene Dateien\Programmieren\AG Heine Hiwi\Rohdaten\control_R1-3-Data.csv")
        return
        while (line := sys.stdin.readline().strip("\n")) != "":
            args = line.split("\t")
            print(line)
            match args[0].lower():
                case "open":
                    if len(args) != 2:
                        print("[TraceSelector] syntax: open [path]")
                        continue
                    path = args[1].strip("'").strip('"')
                    if not pathlib.Path(args[1]).exists():
                        print(f"[TraceSelector] File {path} does not exists")
                        continue
                    print(f"[TraceSelector] Opening file {path}")
                    API.OpenFile(path)
                case _:
                    print(f"[TraceSelector] Unknown command '{args[0]}'")

 


class API:
    def OpenFile(path: str):
        App.main.open_file(path)

if __name__ == "__main__":
    App.start()
