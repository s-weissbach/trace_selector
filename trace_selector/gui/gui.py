from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QToolBar,
    QStatusBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QSlider,
    QMessageBox,
    QStackedLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont
from PyQt6 import QtWebEngineWidgets

from .settingswindow import SettingsWindow
from .add_window import AddWindow
from .api import API
from ..utils.trace_data import SynapseResponseData
from ..utils.threshold import compute_threshold
from ..utils.plot import trace_plot
from ..detection.peak_detection import peak_detection_scipy

import os
from typing import Union
import platformdirs
from pathlib import Path

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
asset_path = os.path.join(parent_directory, "assets")


class MainWindow(QMainWindow):
    def __init__(self, settings):
        super(MainWindow, self).__init__()
        # --- settings ---
        self.settings = settings

        # --- variables ---
        self.file_path: Path|None = None # The current path to the file
        self.synapse_response = SynapseResponseData(self)

        # load weights for CNN
        if self.is_ml_detection_activated():
            success = self.model.load_weights(str(self.get_setting("model_path")))
            if not success:
                self.settings.configuration["th_detection"] = True
                self.settings.configuration["ml_detection"] = False
        stim_frames = self.get_setting("stim_frames")
        self.stim_frames = (
            sorted([int(frame) for frame in stim_frames.split(",")])
            if len(stim_frames) > 0
            else []
        )

        # --- function calls ---
        self.setup_gui()
        self.showMaximized()

        self.api = API(self)

    # --- lazy loading

    @property
    def model(self):
        # Introduced by Andreas to lazy load torch, as it contributes around 50 % to loading time
        if self._model is None:
            from ..detection.model_wraper import torch_model
            self._model = torch_model()

    # --- gui ---

    def setup_gui(self):
        self.setWindowTitle("Trace Selector")

        # toolbar
        toolbar = QToolBar("Toolbar")
        self.addToolBar(toolbar)

        # status bar
        self.setStatusBar(QStatusBar(self))

        # main 'tab'
        main_wrapper_widget = QWidget()
        self.main_layout = QVBoxLayout()
        main_wrapper_widget.setLayout(self.main_layout)

        # settings 'tab'
        settings_wrapper_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_wrapper_widget.setLayout(settings_layout)

        # stack layout
        stack_wrapper_widget = QWidget()
        stack_layout = QStackedLayout()
        stack_layout.addWidget(main_wrapper_widget)
        stack_layout.addWidget(settings_wrapper_widget)
        stack_wrapper_widget.setLayout(stack_layout)

        # set stack layout as central widget
        self.setCentralWidget(stack_wrapper_widget)

        # toolbar buttons

        # open
        button_open = QAction(
            QIcon(os.path.join(asset_path, "open.svg")), "Open file (CTRL + O)", self
        )
        button_open.setStatusTip(
            "Open a file containing traces using your file system (CTRL + O)"
        )
        button_open.triggered.connect(self.open_file_qt)
        button_open.setShortcut(QKeySequence("Ctrl+o"))
        toolbar.addAction(button_open)

        # save
        button_save = QAction(
            QIcon(os.path.join(asset_path, "save.svg")),
            "Save your work (CTRL + S)",
            self,
        )
        button_save.setStatusTip(
            "Saves all traces up to this point and skips the rest (CTRL + S)"
        )
        button_save.triggered.connect(self.skip_rest)
        button_save.setShortcut(QKeySequence("Ctrl+s"))
        toolbar.addAction(button_save)

        # settings
        button_settings = QAction(
            QIcon(os.path.join(asset_path, "settings.svg")), "Open settings (S)", self
        )
        button_settings.setStatusTip(
            "Make the Synapse Selector experience your own by adjusting settings (S)"
        )
        button_settings.triggered.connect(lambda: stack_layout.setCurrentIndex(1))
        button_settings.setShortcut(QKeySequence("s"))
        toolbar.addAction(button_settings)

        # spacer between settings and navigation
        toolbar.addSeparator()

        # back
        button_back = QAction(
            QIcon(os.path.join(asset_path, "back.svg")),
            "Go back to previous sample (B)",
            self,
        )
        button_back.setStatusTip("Go back to the previous trace (B)")
        button_back.triggered.connect(self.back)
        button_back.setShortcut(QKeySequence("b"))
        toolbar.addAction(button_back)

        # discard
        button_discard = QAction(
            QIcon(os.path.join(asset_path, "trash.svg")), "Discard sample (Q)", self
        )
        button_discard.setStatusTip("Discard the current trace (Q)")
        button_discard.triggered.connect(self.discard_trace)
        button_discard.setShortcut(QKeySequence("q"))
        toolbar.addAction(button_discard)

        # keep
        button_keep = QAction(
            QIcon(os.path.join(asset_path, "keep.svg")), "Keep sample (E)", self
        )
        button_keep.setStatusTip("Keep the current trace (E)")
        button_keep.triggered.connect(self.keep_trace)
        button_keep.setShortcut(QKeySequence("e"))
        toolbar.addAction(button_keep)

        # add separator between navigation and editing
        toolbar.addSeparator()

        # add
        self.button_add = QAction(
            QIcon(os.path.join(asset_path, "peak.svg")), "Edit responses (W)", self
        )
        self.button_add.setStatusTip(
            "Edit responses by adding new ones or removing existing ones (W)"
        )
        self.set_add_button_functionality()
        self.button_add.setShortcut(QKeySequence("w"))
        self.button_add.triggered.connect(self.open_add_window)
        toolbar.addAction(self.button_add)

        toolbar.addSeparator()

        # file path
        font = QFont()
        font.setPointSize(12)

        self.file_path_label = QLabel("Current open file: ")
        self.file_path_label.setFont(font)

        # state indicator
        self.current_state_indicator = QLabel("")
        self.current_state_indicator.setFont(font)

        # current ROI
        self.current_roi_label = QLabel("Current ROI:")

        # bar above plot
        bar_layout = QHBoxLayout()
        bar_layout.addWidget(self.file_path_label)
        bar_layout.addWidget(self.current_state_indicator)
        bar_layout.addStretch()
        bar_layout.addWidget(self.current_roi_label)

        self.bar_layout_widget_wrapper = QWidget()
        self.bar_layout_widget_wrapper.setLayout(bar_layout)
        self.main_layout.addWidget(self.bar_layout_widget_wrapper)

        # plot
        self.trace_plot = QtWebEngineWidgets.QWebEngineView(self)
        self.trace_plot.hide()

        # detection slider
        self.threshold_label = QLabel("Current Prediction Threshold (ML-based):")

        probability_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold_slider.setMinimumWidth(300)
        self.threshold_slider.setMinimumHeight(40)
        self.threshold_slider.setValue(self.settings.config["threshold_slider_ml"])
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.sliderReleased.connect(self.handle_slider_update)
        # self.threshold_slider.valueChanged.connect()

        self.current_threshold_label = QLabel(f"{self.threshold_slider.value()}%")

        probability_layout.addWidget(self.threshold_label)
        probability_layout.addWidget(self.threshold_slider)
        probability_layout.addWidget(self.current_threshold_label)
        probability_layout.addStretch()

        self.probability_layout_wrapper = QWidget()
        self.probability_layout_wrapper.setLayout(probability_layout)
        self.probability_layout_wrapper.hide()

        # startup label
        self.startup_label = QLabel("Open up a file with traces using the toolbar.")
        self.startup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font.setBold(True)
        self.startup_label.setFont(font)
        self.main_layout.addWidget(self.startup_label)

        self.apply_main_stretch()

        self.add_window = AddWindow(
            add_handler=self.add_response,
            parent=self,
            close_handler=self.close_add_window,
        )

        self.settings_window = SettingsWindow(
            self.settings, self, lambda: stack_layout.setCurrentIndex(0)
        )
        settings_layout.addWidget(self.settings_window)

        if self.synapse_response.file_opened:
            self.plot()

    # --- slot functions ---

    def handle_slider_update(self):
        self.settings_window.update_ml_slider_value(self.threshold_slider.value())
        self.current_threshold_label.setText(f"{self.threshold_slider.value()}%")

    def refresh_slider(self):
        self.threshold_slider.setValue(self.settings.config["threshold_slider_ml"])
        self.current_threshold_label.setText(f"{self.threshold_slider.value()}%")

    def add_response(self, peak_value):
        """
        Add a response manually that was not detected by the regular peak detection
        """
        # check if peak is valid
        self.synapse_response.add_manual_peak(peak_value)

        # add response to plot
        changed = False
        for i, peak in enumerate(self.synapse_response.peaks):
            if peak in self.labels:
                continue
            changed = True
            self.labels.append(peak)
            self.tr_plot.add_annotation(peak)

        if changed:
            self.tr_plot.reload_plot()
            self.trace_plot.setHtml(self.tr_plot.fig.to_html(include_plotlyjs="cdn"))

    def back(self):
        """
        Go one trace plot back
        """
        if not self.synapse_response:
            return

        success = self.synapse_response.back()
        if success:
            self.next()

    def keep_trace(self):
        """
        Select trace as a trace that is kept.
        """
        if not self.synapse_response:
            return

        self.synapse_response.keep(
            self.settings.config["select_responses"],
            self.settings.config["frames_for_decay"],
            self.add_window.get_peak_dict(),
            self.stim_frames,
            self.settings.config["stim_frames_patience_l"],
            self.settings.config["stim_frames_patience_r"],
        )
        self.next()

    def discard_trace(self):
        """
        Put trace to the unselected traces
        """
        if not self.synapse_response:
            return

        self.synapse_response.discard()
        self.next()

    def skip_rest(self):
        """
        Method to skip all remaining traces (these will be appended to discard) and
        open next file.
        """
        if not self.synapse_response:
            return

        response = QMessageBox.question(
            self,
            "Skip Rest",
            "Do you wish skip the remaining traces and save your current results?",
        )
        if response == QMessageBox.StandardButton.No:
            return
        self.synapse_response.discard_rest()
        self.next()

    def close_add_window(self) -> None:
        self.add_window.hide()

    def open_add_window(self) -> None:
        self.close_add_window()
        self.add_window.show()

    def initialize_add_window(self, peaks, new_sample) -> None:
        self.add_window.update_length(len(self.synapse_response.intensity)-1)
        if new_sample:
            self.add_window.reset()
        self.add_window.load_peaks(peaks)

    # --- helper functions ---

    def set_add_button_functionality(self) -> None:
        self.button_add.setEnabled(
            self.settings.config["select_responses"]
            and self.synapse_response.file_opened
        )

    def update_file_path_label(self) -> None:
        self.file_path_label.setText("Current open file: " + self.file_path.name if self.file_path is not None else '')

    def apply_main_stretch(self) -> None:
        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 10)
        self.main_layout.setStretch(2, 1)

    def get_setting(self, setting_key: str) -> Union[str, int, float, bool]:
        return self.settings.config[setting_key]

    def is_ml_detection_activated(self):
        return self.get_setting("ml_detection")

    def is_th_detection_activated(self):
        return self.get_setting("th_detection")

    def reset(self) -> None:
        self.switch_to_start_layout()
        self.close_add_window()
        self.file_path = None
        self.update_file_path_label()

    def open_file_qt(self):
        self.open_file()

    def open_file(self, path: str|None = None) -> None:
        """
        Opens a new file holding the synaptic responses.
        This file should have meta columns (that will be ignored) and appended to the
        resulting output dataframes and response columns.
        All responses columns will be plotted.
        """
        if path is None:
            if (path := QFileDialog.getOpenFileName(
                    caption="Select Input File",
                    directory=str(self.file_path.parent) if self.file_path is not None else None,
                    filter="Table(*.txt *.csv *.xlsx *.xls)",
                )[0]) == "":
                warning = QMessageBox(self)
                warning.setWindowTitle("Warning")
                warning.setText("No file has been selected")
                warning.exec()
                return
        self.file_path = Path(path)
        self.update_file_path_label()

        self.synapse_response.open_file(
            self.file_path,
            self.get_setting("meta_columns"),
            self.get_setting("normalization_use_median"),
            self.get_setting("normalization_sliding_window_size"),
        )
        self.labels = []

        self.switch_to_main_layout()
        self.plot()
        self.current_roi_label.setText(
            f"Current ROI: {self.synapse_response.columns[self.synapse_response.idx]}"
        )

    def add_slider(self):
        if self.is_ml_detection_activated():
            self.remove_slider()

            self.probability_layout_wrapper.show()
            self.main_layout.addWidget(self.probability_layout_wrapper)
            self.main_layout.setAlignment(
                self.probability_layout_wrapper,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            )

    def remove_slider(self):
        try:
            self.main_layout.removeWidget(self.probability_layout_wrapper)
            self.probability_layout_wrapper.hide()
        except Exception as e:
            None

    def switch_to_main_layout(self):
        self.main_layout.removeWidget(self.startup_label)
        self.startup_label.hide()

        self.trace_plot.show()
        self.main_layout.addWidget(self.trace_plot)

        self.add_slider()

        self.apply_main_stretch()
        self.set_add_button_functionality()

    def switch_to_start_layout(self):
        self.main_layout.removeWidget(self.trace_plot)
        self.trace_plot.hide()

        self.remove_slider()

        self.startup_label.show()
        self.main_layout.addWidget(self.startup_label)

        self.apply_main_stretch()
        self.set_add_button_functionality()

    def plot(self, new_sample=True) -> None:
        """
        Plots a trace of the response that a specific Synapse gave.
        This is done by creating a instance of trace_plot (plot.py),
        that handels all operations of the figure.
        """

        # check to load normalized or unnormalized trace
        trace = (
            self.synapse_response.norm_intensity
            if self.get_setting("normalized_trace")
            else self.synapse_response.intensity
        )

        self.threshold = compute_threshold(
            trace,
            self.get_setting("threshold_mult"),
        )

        self.peak_detection()
        self.add_window.update_information(
            self.model.preds if self.is_ml_detection_activated() else [],
            trace,
        )
        self.initialize_add_window(self.synapse_response.peaks, new_sample=new_sample)

        # create plot depending on mode
        self.tr_plot = trace_plot(
            time=self.synapse_response.time,
            intensity=trace,
            threshold=self.threshold,
            threshold_detection_activated=self.is_th_detection_activated(),
            probabilities=self.model.preds if self.is_ml_detection_activated() else [],
            always_show_threshold=self.get_setting("always_show_threshold"),
        )
        self.tr_plot.create_plot()

        # add responses
        if self.settings.config["select_responses"]:
            self.stim_frames = self.settings_window.stimframes
            if self.settings.config["stim_used"]:
                if (
                    self.settings.config["use_manual_stim_frames"]
                    and self.get_setting("stim_frames") != ""
                ):
                    self.tr_plot.add_stimulation_window(
                        self.stim_frames, self.settings.config["stim_frames_patience_l"], self.settings.config["stim_frames_patience_r"]
                    )
                else:
                    self.tr_plot.add_stimulation_window(
                        [],
                        self.settings.config["stim_frames_patience_l"],
                        self.settings.config["stim_frames_patience_r"],
                        self.get_setting("stim_frames_start"),
                        self.get_setting("stim_frames_step"),
                    )
                    length = len(self.synapse_response.time)
                    num_steps = length // self.get_setting("stim_frames_step")
                    # if automaticly detected stim frames - update stim frames
                    # for later analysis
                    step_size = self.get_setting("stim_frames_step")
                    stimulation_start = self.get_setting("stim_frames_start")
                    self.stim_frames = [
                        step * step_size + stimulation_start
                        for step in range(num_steps)
                        if step * step_size + 2 * stimulation_start <= length
                    ]

        self.labels = self.tr_plot.add_peaks(
            self.add_window.get_peak_dict(), self.settings.config["nms"]
        )

        # set plot
        self.trace_plot.setHtml(self.tr_plot.fig.to_html(include_plotlyjs="cdn"))
        self.current_state_indicator.setText(self.synapse_response.return_state())

        if not self.is_ml_detection_activated():
            self.remove_slider()
        else:
            self.add_slider()

    def next(self):
        """
        Opens next trace and if this is the last trace, it opens a new file.
        """
        if not self.synapse_response.file_opened:
            return

        self.add_window.reset()

        # reinitalize labels
        self.labels = []
        # check if end of file
        if self.synapse_response.end_of_file():
            # if the output paths are not set, the user needs to set them now
            if self.settings.config["output_filepath"] == "":
                warning = QMessageBox(self)
                warning.setWindowTitle("Warning")
                warning.setText(
                    "No output path has been set. Please select it before your files can be saved."
                )
                warning.exec()
                self.settings.get_output_folder(self)
                # abort next() if output paths have not been set
                if self.settings.config["output_filepath"] == "":
                    warning = QMessageBox(self)
                    warning.setWindowTitle("Warning")
                    warning.setText(
                        "No output path has been set. Your data has not been lost. Make sure to select an output path."
                    )
                    warning.exec()
                    return

            # tell the user that the file was done and it has been saved
            msg = QMessageBox(self)
            msg.setWindowTitle("Info")
            msg.setText(
                "You reached the end of the file. Your data will be saved at the set output path"
            )
            msg.exec()
            self.synapse_response.save(self.stim_frames, self.settings.config)
            # self.clear_selection_buttons()
            self.reset()
            self.open_file()
            return

        # advance to next trace if file isn't at eof
        self.synapse_response.next(
            self.get_setting("normalization_use_median"),
            self.get_setting("normalization_sliding_window_size"),
        )
        self.plot()
        self.current_roi_label.setText(
            f"Current ROI: {self.synapse_response.columns[self.synapse_response.idx]}"
        )
        # = QLabel("Current ROI:")
        # self.clear_selection_buttons()

    def peak_detection(self):
        """
        Runs peak detection and hands peaks to synapse_response data class.
        """
        peaks = []
        if self.is_th_detection_activated():
            peaks += peak_detection_scipy(
                intensity=self.synapse_response.norm_intensity,
                threshold=self.threshold,
                prominence=self.settings.config["threshold_prominence"],
                minDistance=self.settings.config["threshold_mindistance"],
                stim_used=self.settings.config["stim_used"],
                stim_frames=self.stim_frames,
                patience_l=self.settings.config["stim_frames_patience_l"],
                patience_r=self.settings.config["stim_frames_patience_r"],
            )

        if self.is_ml_detection_activated():
            if not self.model.weights_loaded:
                self.model.load_weights(self.settings.config["model_path"])
            peaks += self.model.predict(
                self.synapse_response.norm_intensity,
                self.settings.config["threshold_slider_ml"] / 100,
            )

        unique_peaks = list(set(peaks))
        unique_peaks.sort()

        # nms
        if self.get_setting("nms"):
            result_arr = []
            processed_peaks = []
            window_size = self.get_setting("nms_window")

            # iterate over all peaks
            for idx, peak in enumerate(unique_peaks):
                if peak in processed_peaks:
                    continue
                # get all peaks within the nms window
                # as we are starting from the front we only have to look half the window size towards the front
                tmp_arr = []
                for inner_idx in range(idx, len(unique_peaks)):
                    if unique_peaks[inner_idx] <= peak + (window_size // 2):
                        tmp_arr.append(unique_peaks[inner_idx])

                # element itself is always tmp_arr
                max_idx = tmp_arr[0]

                for peak_idx in tmp_arr:
                    if (
                        self.synapse_response.norm_intensity[peak_idx]
                        >= self.synapse_response.norm_intensity[max_idx]
                    ):
                        max_idx = peak_idx
                    processed_peaks.append(peak_idx)

                result_arr.append(max_idx)

            unique_peaks = result_arr

        self.synapse_response.add_automatic_peaks(unique_peaks)

    def update_probability_label(self) -> None:
        # self.current_threshold.setText(f"{self.threshold_slider.value()}%")
        automatic_peaks = self.model.update_predictions(
            self.settings.config["threshold_slider_ml"] / 100
        )
        self.synapse_response.automatic_peaks = []
        self.synapse_response.add_automatic_peaks(automatic_peaks)
        self.plot(new_sample=False)
