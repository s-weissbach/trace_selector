from synapse_selector.gui.gui import MainWindow
from synapse_selector.utils.configuration import gui_settings
from synapse_selector.detection.model_zoo import ModelZoo

from PyQt6.QtWidgets import QApplication
import sys
import os
import platform


def main():
    # get modelzoo directory
    if platform.system() == "Windows":
        modelzoo_folder = os.path.join(
            str(os.environ.get("USERPROFILE")), ".synapse_selector_modelzoo"
        )
    else:
        modelzoo_folder = os.path.join(
            str(os.environ.get("HOME")), ".synapse_selector_modelzoo"
        )
    # check for available ML models
    modelzoo = ModelZoo(modelzoo_folder)
    modelzoo.check_for_updates()
    # initalize settings
    settings = gui_settings(modelzoo)
    # initalize GUI
    app = QApplication(sys.argv)
    main = MainWindow(settings)
    # main = UiWindow(settings)
    main.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
