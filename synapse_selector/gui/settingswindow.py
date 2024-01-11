from PyQt6.QtWidgets import (
    QLabel,
    QFrame,
    QSlider,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
    QTabWidget,
)
from PyQt6.QtCore import Qt
import warnings


class SettingsWindow(QWidget):
    def __init__(self, settings, parent, goBackHandler):
        super().__init__()
        self.parent = parent
        self.settings = settings

        page_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        page_layout.addWidget(self.tab_widget)

        self.setLayout(page_layout)

        # --- general ---

        general_layout = QVBoxLayout()

        self.output_folder_path_label = QLabel(
            "Output Folder Path: " + self.settings.config["output_filepath"]
        )
        general_layout.addWidget(self.output_folder_path_label)

        set_path_layout = QHBoxLayout()
        self.button_set_output_path = QPushButton("Set Output Folder Path")
        self.button_set_output_path.clicked.connect(self.set_output_path)
        set_path_layout.addStretch()
        set_path_layout.addWidget(self.button_set_output_path)
        set_path_layout.addStretch()

        self.button_reset_output_path = QPushButton("Reset Output Folder Path")
        self.button_reset_output_path.clicked.connect(self.reset_output_path)
        set_path_layout.addStretch()
        set_path_layout.addWidget(self.button_reset_output_path)
        set_path_layout.addStretch()
        general_layout.addLayout(set_path_layout)

        self.add_line_to_layout(general_layout)

        self.xlsx_export_box = QCheckBox("Export as .xlsx")
        self.xlsx_export_box.setChecked(self.settings.config["export_xlsx"])
        self.xlsx_export_box.clicked.connect(self.settings_value_changed)
        general_layout.addWidget(self.xlsx_export_box)

        general_layout.addStretch()

        general_wrapper_widget = QWidget()
        general_wrapper_widget.setLayout(general_layout)

        # --- response settings ---
        response_layout = QVBoxLayout()

        peak_detection_type_label = QLabel("Select Detection Method:")
        response_layout.addWidget(peak_detection_type_label)

        dropdown_layout = QHBoxLayout()
        self.peak_detection_type = QComboBox()
        self.peak_detection_type.addItems(["Thresholding", "ML-based"])
        if self.settings.config["peak_detection_type"] == "Thresholding":
            idx = 0
        else:
            idx = 1
        self.peak_detection_type.setCurrentIndex(idx)
        self.peak_detection_type.currentIndexChanged.connect(
            self.settings_value_changed
        )
        dropdown_layout.addWidget(self.peak_detection_type)
        dropdown_layout.addStretch()
        response_layout.addLayout(dropdown_layout)

        self.ml_model_used = QLabel("Select Deep Learning Model:")
        response_layout.addWidget(self.ml_model_used)

        model_dropdown_layout = QHBoxLayout()
        self.ml_model = QComboBox()
        self.ml_model.addItems(self.settings.modelzoo.available_models.keys())
        self.ml_model.setCurrentIndex(0)
        self.ml_model.currentIndexChanged.connect(self.settings_value_changed)
        model_dropdown_layout.addWidget(self.ml_model)
        model_dropdown_layout.addStretch()
        response_layout.addLayout(model_dropdown_layout)

        self.threshold_label = QLabel("Current Prediction Threshold (ML-based):")
        response_layout.addWidget(self.threshold_label)

        probability_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold_slider.setMinimumWidth(300)
        self.threshold_slider.setMinimumHeight(40)
        self.threshold_slider.setValue(settings.config["threshold_slider_ml"])
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.valueChanged.connect(self.settings_value_changed)

        self.current_threshold_label = QLabel(f"{self.threshold_slider.value()}%")

        probability_layout.addWidget(self.threshold_slider)
        probability_layout.addWidget(self.current_threshold_label)
        probability_layout.addStretch()

        response_layout.addLayout(probability_layout)

        self.add_line_to_layout(response_layout)

        tau_desc = QLabel("Time window for tau computation:")
        # tau_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        response_layout.addWidget(tau_desc)

        frames_for_decay_layout = QHBoxLayout()
        self.frames_for_decay = QSpinBox()
        self.frames_for_decay.setValue(self.settings.config["frames_for_decay"])
        self.frames_for_decay.setToolTip(
            "In the timeframe from peak to the value set, the program will search for the minimum and compute the decay constant tau."
        )
        self.frames_for_decay.valueChanged.connect(self.settings_value_changed)
        frames_for_decay_layout.addWidget(self.frames_for_decay)
        frames_for_decay_layout.addStretch()
        response_layout.addLayout(frames_for_decay_layout)

        self.add_line_to_layout(response_layout)

        self.normalized_trace_toggle = QCheckBox("Show normalized trace")
        self.normalized_trace_toggle.setChecked(
            self.settings.config["normalized_trace"]
        )
        self.normalized_trace_toggle.clicked.connect(self.settings_value_changed)
        response_layout.addWidget(self.normalized_trace_toggle)

        self.activate_response_selection = QCheckBox("Enable response editing")
        self.activate_response_selection.setChecked(
            self.settings.config["select_responses"]
        )
        self.activate_response_selection.stateChanged.connect(
            self.settings_value_changed
        )
        response_layout.addWidget(self.activate_response_selection)

        self.non_max_supression_button = QCheckBox("Use Non-Maximum Supression")
        self.non_max_supression_button.setChecked(self.settings.config["nms"])
        self.use_nms = self.settings.config["nms"]
        self.non_max_supression_button.stateChanged.connect(self.settings_value_changed)
        response_layout.addWidget(self.non_max_supression_button)

        self.compute_ppr = QCheckBox("Compute PPR")
        self.compute_ppr.setChecked(self.settings.config["compute_ppr"])
        self.compute_ppr.stateChanged.connect(self.settings_value_changed)
        response_layout.addWidget(self.compute_ppr)

        response_layout.addStretch()

        response_wrapper_widget = QWidget()
        response_wrapper_widget.setLayout(response_layout)

        # --- threshold settings ---

        threshold_layout = QVBoxLayout()
        threshold_start_desc = QLabel("Baseline start:")
        # threshold_start_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        threshold_layout.addWidget(threshold_start_desc)

        self.threshold_start_input = QSpinBox()
        self.threshold_start_input.setToolTip(
            "Baseline calculation for threshold starts from this frame."
        )
        self.threshold_start_input.setValue(self.settings.config["threshold_start"])
        self.threshold_start_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_start_input)

        threshold_stop_desc = QLabel("Baseline stop:")
        # threshold_stop_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold_layout.addWidget(threshold_stop_desc)

        self.threshold_stop_input = QSpinBox()
        self.threshold_stop_input.setToolTip(
            "Baseline calculation for threshold ends at this frame."
        )
        self.threshold_stop_input.setValue(self.settings.config["threshold_stop"])
        self.threshold_stop_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_stop_input)

        threshold_desc = QLabel("Threshold multiplier:")
        # threshold_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold_layout.addWidget(threshold_desc)

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setToolTip(
            "Threshold is calculated based on this multiplier."
        )
        self.threshold_input.setSingleStep(self.settings.config["threshold_step"])
        self.threshold_input.setValue(self.settings.config["threshold_mult"])
        self.threshold_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_input)

        self.threshold_wrapper_widget = QWidget()
        self.threshold_wrapper_widget.setLayout(threshold_layout)

        threshold_layout.addStretch()

        # --- stimulation settings ---

        stimulation_layout = QVBoxLayout()

        self.stim_used_box = QCheckBox("Enable Stimulation")
        self.stim_used_box.setChecked(self.settings.config["stim_used"])
        self.stim_used_box.stateChanged.connect(self.settings_value_changed)
        stimulation_layout.addWidget(self.stim_used_box)

        self.stimframes_label = QLabel("Stimulation Frames")
        stimulation_layout.addWidget(self.stimframes_label)

        stimframes_input_layout = QHBoxLayout()
        self.stimframes_input = QLineEdit(self.settings.config["stim_frames"])
        self.stimframes_input.editingFinished.connect(self.settings_value_changed)
        stimframes_input_layout.addWidget(self.stimframes_input)
        stimframes_input_layout.addStretch()
        stimulation_layout.addLayout(stimframes_input_layout)

        self.patience_label = QLabel("Patience")
        stimulation_layout.addWidget(self.patience_label)

        patience_input_layout = QHBoxLayout()
        self.patience_input = QSpinBox()
        self.patience_input.setValue(self.settings.config["stim_frames_patience"])
        self.patience_input.editingFinished.connect(self.settings_value_changed)
        self.patience_input.valueChanged.connect(self.settings_value_changed)
        patience_input_layout.addWidget(self.patience_input)
        patience_input_layout.addStretch()
        stimulation_layout.addLayout(patience_input_layout)

        stimulation_layout.addStretch()

        stimulation_wrapper_widget = QWidget()
        stimulation_wrapper_widget.setLayout(stimulation_layout)

        # --- buttons ---

        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Back")
        cancel_btn.clicked.connect(goBackHandler)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        page_layout.addLayout(button_layout)

        self.tab_widget.addTab(general_wrapper_widget, "General")
        self.tab_widget.addTab(response_wrapper_widget, "Detection")
        self.tab_widget.addTab(self.threshold_wrapper_widget, "Threshold Settings")
        self.tab_widget.addTab(stimulation_wrapper_widget, "Stimulation")

        self.tab_widget.setTabEnabled(
            2, self.settings.config["peak_detection_type"] == "Thresholding"
        )

    def reset_output_path(self):
        self.settings.config["output_filepath"] = ""
        self.settings_value_changed()
        self.update_output_path("")

    def add_line_to_layout(self, layout):
        # Add a horizontal line
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    def set_output_path(self):
        self.settings.get_output_folder(self)
        self.settings_value_changed()
        self.update_output_path(self.settings.config["output_filepath"])

    def update_output_path(self, path: str):
        self.output_folder_path_label.setText("Output Folder Path: " + path)

    def settings_value_changed(self) -> None:
        """
        Whenever any setting is changed this function is called and notes that
        change in the settings_.config dictionary, that is used internally to
        provide the user set configurations.
        """
        # update all values that might have been changed
        self.settings.config["threshold_mult"] = self.threshold_input.value()
        self.settings.config["threshold_start"] = self.threshold_start_input.value()
        self.settings.config["threshold_stop"] = self.threshold_stop_input.value()
        self.settings.config["stim_frames_patience"] = self.patience_input.value()
        self.settings.config["frames_for_decay"] = self.frames_for_decay.value()
        self.settings.config["stim_frames"] = self.stimframes_input.text()
        self.settings.config[
            "peak_detection_type"
        ] = self.peak_detection_type.currentText()
        model_path = self.settings.modelzoo.available_models[
            self.ml_model.currentText()
        ]["filepath"]
        self.settings.config["model_path"] = model_path
        self.settings.config["nms"] = self.non_max_supression_button.isChecked()
        self.settings.config["stim_used"] = self.stim_used_box.isChecked()
        self.settings.config[
            "select_responses"
        ] = self.activate_response_selection.isChecked()
        self.settings.config["compute_ppr"] = self.compute_ppr.isChecked()
        self.settings.config["export_xlsx"] = self.xlsx_export_box.isChecked()
        self.settings.config[
            "normalized_trace"
        ] = self.normalized_trace_toggle.isChecked()
        self.settings.config["threshold_slider_ml"] = self.threshold_slider.value()

        self.current_threshold_label.setText(f"{self.threshold_slider.value()}%")

        if len(self.settings.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []

        self.handle_settings_toggle()
        self.check_patience()

        if (
            self.settings.config["peak_detection_type"] == "ML-based"
            and self.settings.config["model_path"] == ""
        ):
            warnings.warn("No model selected. Will switch to thresholding.")
            self.settings.config["peak_detection_type"] = "Thresholding"

        # update settings
        self.parent.settings = self.settings
        self.settings.write_settings()
        self.parent.stimframes = self.stimframes

        # replot whenever any setting is changed
        if self.parent.synapse_response.file_opened:
            self.parent.plot(new_sample=False)

        # update threshold slider in main window
        self.parent.refresh_slider()

    def check_patience(self) -> None:
        self.patience_input.setStyleSheet("")
        if not self.compute_ppr.isChecked() or len(self.stimframes) <= 1:
            return
        min_distance = self.stimframes[1] - self.stimframes[0]
        for i in range(len(self.stimframes) - 1):
            if self.stimframes[i + 1] - self.stimframes[i] < min_distance:
                min_distance = self.stimframes[i + 1] - self.stimframes[i]
        if min_distance < self.settings.config["stim_frames_patience"]:
            self.patience_input.setStyleSheet(
                "QSpinBox" "{" "background : #ff5959;" "}"
            )

    def handle_settings_toggle(self) -> None:
        if self.settings.config["peak_detection_type"] == "ML-based":
            self.ml_model.setEnabled(True)
            self.ml_model_used.setEnabled(True)
            self.threshold_label.setEnabled(True)
            self.current_threshold_label.setEnabled(True)
            self.threshold_slider.setEnabled(True)

            self.tab_widget.setTabEnabled(2, False)
            self.threshold_wrapper_widget.setEnabled(False)
        else:
            self.ml_model.setEnabled(False)
            self.ml_model_used.setEnabled(False)
            self.threshold_label.setEnabled(False)
            self.current_threshold_label.setEnabled(False)
            self.threshold_slider.setEnabled(False)

            self.tab_widget.setTabEnabled(2, True)
            self.threshold_wrapper_widget.setEnabled(True)

        if self.settings.config["stim_used"]:
            self.stimframes_input.setEnabled(True)
            self.stimframes_label.setEnabled(True)
            self.compute_ppr.setEnabled(True)
            self.patience_label.setEnabled(True)
            self.patience_input.setEnabled(True)
        else:
            self.stimframes_input.setEnabled(False)
            self.stimframes_label.setEnabled(False)
            self.patience_label.setEnabled(False)
            self.patience_input.setEnabled(False)
            self.compute_ppr.setEnabled(False)

        # activate add response button depending on setting
        if self.settings.config["select_responses"]:
            self.parent.button_add.setEnabled(True)
            self.compute_ppr.setEnabled(True)
            self.non_max_supression_button.setEnabled(True)
        else:
            self.parent.button_add.setDisabled(True)
            self.compute_ppr.setEnabled(False)
            self.non_max_supression_button.setEnabled(False)

    # this is being called by the parent to synchronise the threshold slider value
    def update_ml_slider_value(self, value) -> None:
        self.settings.config["threshold_slider_ml"] = value
        self.threshold_slider.setValue(value)
        self.settings_value_changed()
