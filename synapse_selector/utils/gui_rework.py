from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QToolBar,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6 import QtWebEngineWidgets

import os

file_path = os.path.dirname(__file__)
asset_path = '/'.join(file_path.split('/')[0:-1]) + '/assets'


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # --- variables ---
        self.directory = None

        # --- layout ---
        self.setWindowTitle("Synapse Selector")

        label = QLabel("Hello!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(label)

        # toolbar
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # status bar
        self.setStatusBar(QStatusBar(self))

        # layouts
        main_layout = QVBoxLayout()
        wrapper_widget = QWidget()

        # toolbar buttons
        # open
        button_open = QAction(QIcon(os.path.join(asset_path, 'open.svg')), 'Open file', self)
        button_open.setStatusTip('Open a file containing traces using your file system')
        button_open.triggered.connect(self.get_filepath)
        toolbar.addAction(button_open)

        # save
        button_save = QAction(QIcon(os.path.join(asset_path, 'save.svg')), 'Open file', self)
        button_save.setStatusTip('Saves everything already changed')
        # button_save.triggered.connect()
        toolbar.addAction(button_save)

        # settings
        button_settings = QAction(QIcon(os.path.join(asset_path, 'settings.svg')), 'Open file', self)
        button_settings.setStatusTip('Make the Synapse Selector Experience your own')
        # button_settings.triggered.connect()
        toolbar.addAction(button_settings)

        # spacer between settings and navigation
        toolbar.addSeparator()

        # back
        button_back = QAction(QIcon(os.path.join(asset_path, 'back.svg')), 'Open file', self)
        button_back.setStatusTip('Go back to the previous trace')
        # button_back.triggered.connect()
        toolbar.addAction(button_back)

        # trash
        button_trash = QAction(QIcon(os.path.join(asset_path, 'trash.svg')), 'Open file', self)
        button_trash.setStatusTip('Trash the current trace')
        # button_trash.triggered.connect()
        toolbar.addAction(button_trash)

        # keep
        button_trash = QAction(QIcon(os.path.join(asset_path, 'keep.svg')), 'Open file', self)
        button_trash.setStatusTip('Keep the current trace')
        # button_trash.triggered.connect()
        toolbar.addAction(button_trash)

        # add
        button_add = QAction(QIcon(os.path.join(asset_path, 'add.svg')), 'Open file', self)
        button_add.setStatusTip('Add another peak')
        # button_add.triggered.connect()
        toolbar.addAction(button_add)

        # add separator between file path and rest
        toolbar.addSeparator()

        # file path
        self.file_path_label = QLabel('Current open file: ')
        toolbar.addWidget(self.file_path_label)

        # plot
        self.trace_plot = QtWebEngineWidgets.QWebEngineView(self)
        main_layout.addWidget(self.trace_plot)

        wrapper_widget.setLayout(main_layout)
        self.setCentralWidget(wrapper_widget)

    # --- helper functions ---

    def update_file_path_label(self, filepath: str):
        self.file_path_label.setText('Current open file: ' + filepath)

    # --- slot functions ---

    def get_filepath(self):
        # no directory has been saved
        if self.directory is not None:
            self.filepath = QFileDialog.getOpenFileName(
                caption="Select Input File",
                directory=self.directory,
                filter="Table(*.txt *.csv *.xlsx *.xls)",
            )[0]
        else:
            self.filepath = QFileDialog.getOpenFileName(
                caption="Select Input File",
                filter="Table(*.txt *.csv *.xlsx *.xls)",
            )[0]

        # if no path has been selected, ask whether the programm should be terminated
        if self.filepath == '':
            warning = QMessageBox(self)
            warning.setWindowTitle('Warning')
            warning.setText('No file has been selected')
            warning.exec()

        self.filename = os.path.basename(self.filepath)
        self.directory = os.path.dirname(self.filepath)
        self.update_file_path_label(self.filepath)
