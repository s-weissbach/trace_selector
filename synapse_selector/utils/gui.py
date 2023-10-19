import os
import sys

from PyQt6 import QtWebEngineWidgets
from PyQt6.QtWidgets import (
    QLabel,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QEventLoop
from PyQt6.QtGui import QFont
from .threshold import compute_threshold
from .plot import trace_plot
from .trace_data import synapse_response_data_class
from .peak_detection import peak_detection_scipy
from .settings_gui import SettingsWindow


class ui_window(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings_ = settings
        self.directory = None
        # layout
        mainwindowlayout = QVBoxLayout()
        if self.settings_.config["output_filepath"] == "":
            self.settings_.get_output_folder(self)
        else:
            response = QMessageBox.question(
                self,
                "Outputpath",
                f"Loaded outputpath from previous session {self.settings_.config['output_filepath']}. Change outputpath?",
            )
            if response == QMessageBox.StandardButton.Yes:
                self.settings_.get_output_folder(self)
        if len(self.settings_.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings_.config["stim_frames"].split(",")
            ]
        # ---------------------------------------------------------------------------- #
        #                                     row 1                                    #
        # ---------------------------------------------------------------------------- #
        top_row = QHBoxLayout()
        # status indicator
        self.current_file_label = QLabel("")
        mainwindowlayout.addWidget(self.current_file_label)
        self.current_state_indicator = QLabel("")
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.current_state_indicator.setFont(font)
        top_row.addWidget(self.current_state_indicator)
        top_row.addStretch()
        # skip rest
        skip_rest_btn = QPushButton("Skip Rest")
        skip_rest_btn.setToolTip('Remaining traces are trashed, selection is saved.')
        skip_rest_btn.clicked.connect(self.skip_rest)
        top_row.addWidget(skip_rest_btn)
        # open new file
        open_n_file_btn = QPushButton("Open new File")
        open_n_file_btn.setToolTip('All selections are discarded and new file is opned')
        open_n_file_btn.clicked.connect(self.open_n_file)
        top_row.addWidget(open_n_file_btn)
        mainwindowlayout.addLayout(top_row)
        # ---------------------------------------------------------------------------- #
        #                                     row2                                     #
        # ---------------------------------------------------------------------------- #
        self.trace_plot = QtWebEngineWidgets.QWebEngineView(self)
        self.trace_plot.setMinimumSize(1400, 500)
        mainwindowlayout.addWidget(self.trace_plot)
        # settings
        settingsrow = QHBoxLayout()
        settings_button = QPushButton("settings")
        settings_button.clicked.connect(self.change_settings)
        settingsrow.addWidget(settings_button)
        settingsrow.addStretch()
        mainwindowlayout.addLayout(settingsrow)
        # ---------------------------------------------------------------------------- #
        #                                     row 3                                    #
        # ---------------------------------------------------------------------------- #
        buttonlayout = QHBoxLayout()
        # back
        back_button = QPushButton("back")
        back_button.clicked.connect(self.back)
        buttonlayout.addWidget(back_button)
        buttonlayout.addStretch()
        # trash
        trash_button = QPushButton("trash")
        trash_button.clicked.connect(self.trash_trace)
        buttonlayout.addWidget(trash_button)
        # keep
        keep_button = QPushButton("keep")
        keep_button.clicked.connect(self.keep_trace)
        buttonlayout.addWidget(keep_button)
        mainwindowlayout.addLayout(buttonlayout)
        # ---------------------------------------------------------------------------- #
        #                                     row 4                                    #
        # ---------------------------------------------------------------------------- #
        # --------------------- second layer for spike selection --------------------- #
        # selection box layout
        self.response_selection_layout = QHBoxLayout()
        self.response_input_label = QLabel("Add Response: ")
        self.response_input_label.setEnabled(self.settings_.config["select_responses"])
        self.response_selection_layout.addWidget(self.response_input_label)
        self.response_input = QLineEdit()
        self.response_input.setMaximumWidth(200)
        self.response_input.returnPressed.connect(self.add_response)
        self.response_selection_layout.addWidget(self.response_input)
        self.response_input.setEnabled(self.settings_.config["select_responses"])
        self.response_selection_layout.addStretch()
        mainwindowlayout.addLayout(self.response_selection_layout)
        # --------------------------- dynamic button layout -------------------------- #
        self.response_button_v_layout = QVBoxLayout()
        self.response_button_layout_list = [QHBoxLayout()]
        self.response_button_list = []
        self.response_button_v_layout.addLayout(self.response_button_layout_list[0])
        mainwindowlayout.addLayout(self.response_button_v_layout)
        self.setLayout(mainwindowlayout)
        # select file
        self.get_filepath()
        # load file
        self.open_file()
        # plot
        self.plot()
        self.selected_peaks = []
        if len(self.settings_.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings_.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []
        self.current_layout_count = 0

    def initalize_file(self) -> None:
        """
        Asks user for a new file and opens that file.
        """
        self.get_filepath()
        self.open_file()

    def change_settings(self) -> None:
        self.w = SettingsWindow(self.settings_, self)
        self.w.show()
        loop = QEventLoop()
        self.w.destroyed.connect(loop.quit)
        loop.exec()

    def get_filepath(self):
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
        if self.filepath == "":
            response = QMessageBox.question(
                self, "No file selected", "Do you wish to terminate the programm?"
            )
            # response.setStandardButtons()
            if response == QMessageBox.StandardButton.No:
                self.get_filepath()
            else:
                sys.exit()
        self.current_keep_folder = os.path.join(
            self.settings_.config["keep_folder"], os.path.basename(self.filepath)
        )
        if not os.path.exists(self.current_keep_folder):
            os.mkdir(self.current_keep_folder)
        self.current_trash_folder = os.path.join(
            self.settings_.config["trash_folder"], os.path.basename(self.filepath)
        )
        if not os.path.exists(self.current_trash_folder):
            os.mkdir(self.current_trash_folder)
        self.filename = os.path.basename(self.filepath)
        self.directory = os.path.dirname(self.filepath)
        self.current_file_label.setText(self.filepath)

    def open_file(self):
        """
        Opens a new file holding the synaptic responses.
        This file should have meta columns (that will be ignored) and appended to the
        resulting output dataframes and response columns.
        All responses columns will be plotted.
        """
        self.synapse_response = synapse_response_data_class(
            self.filepath, self.filename, self.settings_.config["meta_columns"]
        )
        self.peak_selection_buttons = []
        self.labels = []

    def plot(self):
        """
        Plots a trace of the response that a specific Synapse gave.
        This is done by creating a instance of trace_plot (plot.py),
        that handels all operations of the figure.
        """
        # ----------------------------- compute threshold ---------------------------- #
        self.threshold = compute_threshold(
            self.settings_.config["stim_used"],
            self.synapse_response.intensity,
            self.settings_.config["threshold_mult"],
            self.settings_.config["threshold_start"],
            self.settings_.config["threshold_stop"],
        )
        # ----------------------------------- plot ----------------------------------- #
        self.tr_plot = trace_plot(
            self.synapse_response.time, self.synapse_response.intensity, self.threshold
        )
        self.tr_plot.create_plot()
        # --------------------------------- responses -------------------------------- #
        if self.settings_.config["select_responses"]:
            if self.settings_.config["stim_used"]:
                self.tr_plot.add_stimulation_window(
                    self.stimframes, self.settings_.config["stim_frames_patience"]
                )
            self.peak_selection()
            selection = [btn.isChecked() for btn in self.peak_selection_buttons]
            self.labels = self.tr_plot.add_peaks(
                self.synapse_response.peaks, self.settings_.config["nms"], selection
            )
        self.trace_plot.setHtml(self.tr_plot.fig.to_html(include_plotlyjs="cdn"))
        self.current_state_indicator.setText(self.synapse_response.return_state())

    def next(self):
        """
        Opens next trace and if this is the las trace, it opens a new file.
        """
        # reinitalize labels
        self.labels = []
        # check if end of file
        if self.synapse_response.end_of_file():
            # if end of file load next file
            self.synapse_response.save(
                self.settings_.config["export_xlsx"],
                self.current_keep_folder,
                self.current_trash_folder,
                self.settings_.config["compute_ppr"],
                self.stimframes,
                self.settings_.config["stim_frames_patience"]
            )
            self.clear_selection_buttons()
            self.initalize_file()
        else:
            self.synapse_response.next()
        self.clear_selection_buttons()
        self.peak_selection_buttons = []
        self.plot()

    def back(self):
        """
        Go one trace plot back
        """
        success = self.synapse_response.back()
        if success:
            self.next()

    def keep_trace(self):
        """
        Select trace as a trace that is kept.
        """
        if self.settings_.config["select_responses"]:
            selection = [
                int(btn.text().split(" ")[1])
                for btn in self.peak_selection_buttons
                if btn.isChecked()
            ]
        else:
            selection = []
        self.synapse_response.keep(self.settings_.config["select_responses"],
                                   self.settings_.config['frames_for_decay'],
                                   selection)
        self.next()

    def trash_trace(self):
        """
        Put trace to the unselected traces
        """
        self.synapse_response.trash()
        self.next()

    def skip_rest(self):
        """
        Method to skip all remaining traces (these will be appended to trash) and
        open next file.
        """
        response = QMessageBox.question(
            self, "Skip Rest", "Do you wish skip the remaining traces?"
        )
        if response == QMessageBox.StandardButton.No:
            return
        self.synapse_response.trash_rest()
        self.next()

    def open_n_file(self):
        """
        Method to open a new file and discarding all selections made for this file.
        """
        response = QMessageBox.question(
            self,
            "Open next File",
            "Do you wish to open new file (Results will not be saved)?",
        )
        if response == QMessageBox.StandardButton.No:
            return
        self.initalize_file()

    def add_response(self):
        """
        Add a response manually that was not detected by the regular peak detection
        """
        # parse peak
        peak = int(self.response_input.text())
        # check if peak is valid
        self.synapse_response.add_manual_peak(peak)
        # ----------------------------- selection buttons ---------------------------- #
        # add label
        if self.current_layout_count > 14:
            self.current_layout_count = 0
            self.current_layout_row += 1
            # if needed add new layout in new row
            if len(self.response_button_layout_list) - 1 <= self.current_layout_row:
                self.response_button_layout_list.append(QHBoxLayout())
                self.response_button_v_layout.addLayout(
                    self.response_button_layout_list[-1]
                )
        self.peak_selection_buttons.append(QCheckBox(f"Peak {peak}"))
        self.peak_selection_buttons[-1].setChecked(True)
        self.response_button_layout_list[self.current_layout_row].addWidget(
            self.peak_selection_buttons[-1]
        )
        self.current_layout_count += 1
        # add response to plot
        self.label_changed()
        # empty QLineEdit
        self.response_input.setText("")

    def peak_detection(self):
        """
        Runs peak detection and hands peaks to synapse_response data class.
        """
        automatic_peaks = peak_detection_scipy(
            self.synapse_response.intensity,
            self.threshold,
            self.settings_.config["stim_used"],
            self.stimframes,
            self.settings_.config["stim_frames_patience"],
        )
        self.synapse_response.add_automatic_peaks(automatic_peaks)

    def peak_selection(self):
        """
        Create button layout for peak selection and toggle buttons (NMS logic).
        """
        self.peak_detection()
        self.clear_selection_buttons()
        self.peak_selection_buttons = []
        # have 10 buttons per layout
        self.current_layout_count = 0
        self.current_layout_row = 0
        if self.settings_.config["nms"]:
            nms_peaks = self.synapse_response.non_max_supression(self.threshold)
        else:
            nms_peaks = []
        for peak in self.synapse_response.peaks:
            if self.current_layout_count > 14:
                self.current_layout_count = 0
                self.current_layout_row += 1
                # if needed add new layout
                if len(self.response_button_layout_list) - 1 <= self.current_layout_row:
                    self.response_button_layout_list.append(QHBoxLayout())
                    self.response_button_v_layout.addLayout(
                        self.response_button_layout_list[-1]
                    )
            self.peak_selection_buttons.append(QCheckBox(f"Peak {peak}"))
            self.response_button_layout_list[self.current_layout_row].addWidget(
                self.peak_selection_buttons[-1]
            )
            if peak in self.synapse_response.manual_peaks:
                self.peak_selection_buttons[-1].setChecked(True)
            elif peak in nms_peaks:
                self.peak_selection_buttons[-1].setChecked(False)
            else:
                self.peak_selection_buttons[-1].setChecked(True)
            self.current_layout_count += 1
        for button in self.peak_selection_buttons:
            button.stateChanged.connect(self.label_changed)

    def label_changed(self) -> None:
        """
        Get changes made in selection to update the trace plot's annotation.
        """
        change_made = False
        for i, peak in enumerate(self.synapse_response.peaks):
            if peak in self.labels:
                continue
            if self.peak_selection_buttons[i].isChecked():
                change_made = True
                self.labels.append(peak)
                self.tr_plot.add_label(peak)
        if change_made:
            self.tr_plot.reload_plot()
            self.trace_plot.setHtml(self.tr_plot.fig.to_html(include_plotlyjs="cdn"))

    def clear_selection_buttons(self) -> None:
        """
        Method to remove all peak selection buttons currently in the layout.
        """
        for button in self.peak_selection_buttons:
            self.response_selection_layout.removeWidget(button)
            button.deleteLater()
            button = None
