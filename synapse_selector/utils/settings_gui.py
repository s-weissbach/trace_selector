from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QWidget,
                             QSpinBox, QCheckBox, QLineEdit, QDoubleSpinBox,
                             QPushButton)
from PyQt6.QtCore import Qt


class SettingsWindow(QWidget):
    def __init__(self, settings, parent):
        super().__init__()
        self.parent = parent
        self.settings_ = settings
        settingslayout = QVBoxLayout()
        # ---------------------------- Threshold settings ---------------------------- #
        threshold_layout = QHBoxLayout()
        threshold_start_desc = QLabel("Baseline start:")
        threshold_start_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold_layout.addWidget(threshold_start_desc)
        self.threshold_start_input = QSpinBox()
        self.threshold_start_input.setToolTip('Baseline calculation for threshold starts from this frame.')
        self.threshold_start_input.setValue(self.settings_.config["threshold_start"])
        self.threshold_start_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_start_input)
        threshold_stop_desc = QLabel("Baseline stop:")
        threshold_stop_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold_layout.addWidget(threshold_stop_desc)
        self.threshold_stop_input = QSpinBox()
        self.threshold_stop_input.setToolTip('Baseline calculation for threshold ends at this frame.')
        self.threshold_stop_input.setValue(self.settings_.config["threshold_stop"])
        self.threshold_stop_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_stop_input)
        # threshold multiplier
        threshold_desc = QLabel("Threshold multiplier:")
        threshold_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        threshold_layout.addWidget(threshold_desc)
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setToolTip('Threshold is calculated based on this multiplier.')
        self.threshold_input.setSingleStep(self.settings_.config["threshold_step"])
        self.threshold_input.setValue(self.settings_.config["threshold_mult"])
        self.threshold_input.valueChanged.connect(self.settings_value_changed)
        threshold_layout.addWidget(self.threshold_input)
        threshold_layout.addStretch()
        settingslayout.addLayout(threshold_layout)
        # ------------------------ response selection settings ----------------------- #
        response_layout = QHBoxLayout()
        self.activate_response_selection = QCheckBox("Select Responses")
        self.activate_response_selection.setChecked(
            self.settings_.config["select_responses"]
        )
        self.activate_response_selection.stateChanged.connect(
            self.settings_value_changed
        )
        response_layout.addWidget(self.activate_response_selection)
        # nms toggle
        self.non_max_supression_button = QCheckBox("Non-Maximum Supression")
        self.non_max_supression_button.setChecked(self.settings_.config["nms"])
        self.non_max_supression_button.setEnabled(
            self.settings_.config["select_responses"]
        )
        self.use_nms = self.settings_.config["nms"]
        self.non_max_supression_button.stateChanged.connect(self.settings_value_changed)
        response_layout.addWidget(self.non_max_supression_button)
        # compute PPR
        self.compute_ppr = QCheckBox("Compute PPR")
        self.compute_ppr.setChecked(self.settings_.config["compute_ppr"])
        self.compute_ppr.stateChanged.connect(self.settings_value_changed)
        response_layout.addWidget(self.compute_ppr)
        tau_desc = QLabel("Time window for tau computation:")
        tau_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        response_layout.addWidget(tau_desc)
        self.frames_for_decay = QSpinBox()
        self.frames_for_decay.setValue(self.settings_.config["frames_for_decay"])
        self.frames_for_decay.setToolTip(
            "In the timeframe from peak to the value set, the program will search for the minimum and compute the decay constant tau.")
        self.frames_for_decay.valueChanged.connect(self.settings_value_changed)
        response_layout.addWidget(self.frames_for_decay)
        response_layout.addStretch()
        settingslayout.addLayout(response_layout)
        # --------------------------- stimulation settings --------------------------- #
        stimulation_layout = QHBoxLayout()
        # stimulation used
        self.stim_used_box = QCheckBox("Stimulation used")
        self.stim_used_box.setChecked(self.settings_.config["stim_used"])
        self.stim_used_box.stateChanged.connect(self.settings_value_changed)
        stimulation_layout.addWidget(self.stim_used_box)
        # stim frames
        self.stimframes_label = QLabel("Stimulation Frames")
        self.stimframes_label.setEnabled(self.settings_.config["stim_used"])
        stimulation_layout.addWidget(self.stimframes_label)
        self.stimframes_input = QLineEdit(self.settings_.config["stim_frames"])
        self.stimframes_input.setMaximumWidth(200)
        self.stimframes_input.setEnabled(self.settings_.config["stim_used"])
        self.stimframes_input.editingFinished.connect(self.settings_value_changed)
        stimulation_layout.addWidget(self.stimframes_input)
        patience_label = QLabel("Patience")
        stimulation_layout.addWidget(patience_label)
        self.patience_input = QSpinBox()
        self.patience_input.setValue(self.settings_.config["stim_frames_patience"])
        self.patience_input.setEnabled(False)
        self.patience_input.editingFinished.connect(self.settings_value_changed)
        self.patience_input.valueChanged.connect(self.settings_value_changed)
        stimulation_layout.addWidget(self.patience_input)
        stimulation_layout.addStretch()
        settingslayout.addLayout(stimulation_layout)
        # xlsx export
        self.xlsx_export_box = QCheckBox("Export as .xlsx")
        self.xlsx_export_box.setChecked(self.settings_.config["export_xlsx"])
        self.xlsx_export_box.clicked.connect(self.settings_value_changed)
        settingslayout.addWidget(self.xlsx_export_box)
        # ------------------------------- close buttons ------------------------------ #
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton('Ok')
        ok_btn.clicked.connect(self.save_and_close)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.close_)
        btn_layout.addWidget(cancel_btn)
        settingslayout.addLayout(btn_layout)
        self.setLayout(settingslayout)
        if len(self.settings_.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings_.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []

    def settings_value_changed(self) -> None:
        """
        Whenever any setting is changed this function is called and notes that
        change in the settings_.config dictionary, that is used internally to
        provide the user set configurations.
        """
        # update all values that might have been changed
        self.settings_.config["threshold_mult"] = self.threshold_input.value()
        self.settings_.config["threshold_start"] = self.threshold_start_input.value()
        self.settings_.config["threshold_stop"] = self.threshold_stop_input.value()
        self.settings_.config["stim_frames_patience"] = self.patience_input.value()
        self.settings_.config["frames_for_decay"] = self.frames_for_decay.value()
        self.settings_.config["stim_frames"] = self.stimframes_input.text()
        if len(self.settings_.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings_.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []
        self.settings_.config["nms"] = self.non_max_supression_button.isChecked()
        self.settings_.config["stim_used"] = self.stim_used_box.isChecked()
        self.settings_.config[
            "select_responses"
        ] = self.activate_response_selection.isChecked()
        self.settings_.config["compute_ppr"] = self.compute_ppr.isChecked()
        self.settings_.config["export_xlsx"] = self.xlsx_export_box.isChecked()
        # ------------------------------- toggle logic ------------------------------- #
        if self.settings_.config["stim_used"]:
            self.stimframes_input.setEnabled(True)
            self.stimframes_label.setEnabled(True)
            self.compute_ppr.setEnabled(True)
            self.patience_input.setEnabled(True)
        else:
            self.stimframes_input.setEnabled(False)
            self.stimframes_label.setEnabled(False)
            self.patience_input.setEnabled(False)
            self.compute_ppr.setEnabled(False)
        if self.settings_.config["select_responses"]:
            self.compute_ppr.setEnabled(True)
            self.non_max_supression_button.setEnabled(True)
        else:
            self.compute_ppr.setEnabled(False)
            self.non_max_supression_button.setEnabled(False)
        self.check_patience()

    def check_patience(self) -> None:
        self.patience_input.setStyleSheet("")
        if not self.compute_ppr.isChecked() or len(self.stimframes) <= 1:
            return
        min_distance = self.stimframes[1] - self.stimframes[0]
        for i in range(len(self.stimframes)-1):
            if self.stimframes[i+1] - self.stimframes[i] < min_distance:
                min_distance = self.stimframes[i+1] - self.stimframes[i]
        if min_distance < self.settings_.config['stim_frames_patience']:
            self.patience_input.setStyleSheet("QSpinBox"
                                              "{"
                                              "background : #ff5959;"
                                              "}")

    def save_and_close(self) -> None:
        self.parent.settings_ = self.settings_
        self.parent.stimframes = self.stimframes
        self.settings_.write_settings()
        if self.settings_.config["select_responses"]:
            self.parent.response_input_label.setEnabled(True)
            self.parent.response_input.setEnabled(True)
        else:
            self.parent.response_input_label.setEnabled(False)
            self.parent.response_input.setEnabled(False)
        self.parent.plot()
        self.close()

    def close_(self) -> None:
        self.close()
