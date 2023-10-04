import os
import json
import platform
from PyQt6.QtWidgets import QFileDialog

import os
import sys

from PyQt6.QtWidgets import QApplication
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
    QVBoxLayout,
)
from PyQt6.QtCore import QEventLoop
from PyQt6.QtGui import QFont
from scipy.signal import find_peaks 
import numpy as np
import numpy as np
import plotly.express as px
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QSpinBox, QCheckBox, QLineEdit, QDoubleSpinBox,
                             QPushButton)
from PyQt6.QtCore import Qt
import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
import numpy as np
import os

class synapse_response_data_class:
    def __init__(self,
                 filepath: str,
                 filename: str,
                 meta_columns: list[str]) -> None:
        self.filename = filename
        if filepath.endswith('.txt') or filepath.endswith('.csv'):
            self.df = pd.read_csv(filepath,sep=',')
        else:
            self.df = pd.read_excel(filepath)
        self.meta_columns = [col for col in self.df.columns if col in meta_columns or is_string_dtype(self.df[col])]
        self.columns = [col for col in self.df.columns if col not in self.meta_columns]
        self.keep_data = []
        self.trash_data = []
        self.idx = 0
        self.last = []
        self.peaks = []
        self.manual_peaks = []
        self.selected_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))
        self.automatic_peaks = []
    
    def __len__(self) -> int:
        '''
        returns number of traces to look at as length.
        '''
        return len(self.columns)

    def return_state(self) -> str:
        '''
        returns index and length of current file and computes percentage of
        sorted traces.
        '''
        percentage = np.round(self.idx / len(self),4)*100
        return f'{self.idx+1}/{len(self)} ({percentage}%)'

    def save(self,
             export_xlsx: bool,
             keep_path: str,
             trash_path: str,
             ppr: bool,
             stimulation_timepoints: list[int],
             patience: int) -> None:
        '''
        Save the sorted trace to the respective keep and trash file and if peak
        detection was used also save the result table for the keep responses.
        '''
        keep_df = self.df[self.meta_columns+self.keep_data]
        trash_df = self.df[self.meta_columns+self.trash_data]
        if export_xlsx:
            keep_df.to_excel(os.path.join(keep_path,f'{self.filename}.xlsx'),index=False)
            trash_df.to_excel(os.path.join(trash_path,f'{self.filename}.xlsx'),index=False)
        elif self.filename.endswith('.xlsx') or self.filename.endswith('.xls'):
            keep_df.to_excel(os.path.join(keep_path,f'{self.filename}.xlsx'),index=False)
            trash_df.to_excel(os.path.join(trash_path,f'{self.filename}.xlsx'),index=False)
        else:
            keep_df.to_csv(os.path.join(keep_path,self.filename),index=False)
            trash_df.to_csv(os.path.join(trash_path,self.filename),index=False)
        if len(self.selected_peaks) > 0:
            
            peak_df = pd.DataFrame(self.selected_peaks,columns=['Filename','ROI#','Frame','abs. Amplitude', 'rel. Amplitude','decay50'])
            if export_xlsx:
                output_name = f"{'.'.join(self.filename.split('.')[:-1])}_responses.xlsx"
                peak_df.to_excel(os.path.join(keep_path,output_name),index=False)
            else:
                output_name = f"{'.'.join(self.filename.split('.')[:-1])}_responses.csv"
                peak_df.to_csv(os.path.join(keep_path,output_name),index=False)
            if ppr:
                ppr_df = paired_pulse_ratio(peak_df,stimulation_timepoints,patience)
                if export_xlsx:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_ppr.xlsx"
                    ppr_df.to_excel(os.path.join(keep_path,output_name),index=False)
                else:
                    output_name = f"{'.'.join(self.filename.split('.')[:-1])}_ppr.csv"
                    ppr_df.to_csv(os.path.join(keep_path,output_name),index=False)

    def next(self) -> None:
        '''
        Go to next trace and load the data
        '''
        self.idx += 1
        self.peaks = []
        self.manual_peaks = []
        self.intensity = self.df[self.columns[self.idx]].to_numpy()
        self.time = np.arange(len(self.intensity))
    
    def back(self) -> bool:
        '''
        Go back one trace and undo the selection. If it is the first trace of
        the file, nothing is done.
        '''
        if self.idx == 0:
            return False
        if self.last[-1] == 'keep':
            _ = self.keep_data.pop()
            _ = self.last.pop()
        else:
            _ = self.trash_data.pop()
            _ = self.last.pop()
        selected_peaks_copy = self.selected_peaks.copy()
        self.selected_peaks = []
        for peak in selected_peaks_copy:
            if peak[1] == self.columns[self.idx-1]:
                continue
            self.selected_peaks.append(peak)
        self.idx -= 2
        return True

    def keep(self,
             select_responses: bool,
             selection: list[int]) -> None:
        '''
        Puts currently viewed trace to the keep data and if peaks selected appends
        them to the selected_peaks.
        '''
        self.keep_data.append(self.columns[self.idx])
        self.last.append('keep')
        if not select_responses:
            return 
        # -------------------------- save selected responses ------------------------- #
        for peak_tp in selection:
            amplitude = self.intensity[peak_tp]
            baseline = np.min(self.intensity[max(0,peak_tp-15):peak_tp])
            relative_height = amplitude-baseline
            relative_height50 = relative_height/2 + baseline
            tmp = np.where(self.intensity[peak_tp:]<relative_height50)[0]
            decay50 = np.nan
            if len(tmp) > 0:
                decay50 = tmp[0]
            self.selected_peaks.append([
                self.filename,
                self.columns[self.idx],
                peak_tp,
                amplitude,
                relative_height,
                decay50
            ])
    
    def trash(self) -> None:
        '''
        Puts currently viewed trace to trash.
        '''
        self.trash_data.append(self.columns[self.idx])
        self.last.append('trash')
    
    def trash_rest(self) -> None:
        '''
        Puts all remaining not seen traces to the trash df.
        '''
        self.trash_data += [self.columns[i] for i in range(self.idx,len(self.columns))]
        self.idx = len(self.columns)-1

    def end_of_file(self) -> bool:
        '''
        Checks whether a next trace can be loaded or end of file will be reached.
        '''
        if self.idx+1 == len(self):
            return True
        return False

    def add_automatic_peaks(self, peaks: list[int]) -> None:
        '''
        Add automatic peaks to peak list.
        '''
        self.automatic_peaks = peaks
        self.peaks = self.automatic_peaks + self.manual_peaks
    
    def add_manual_peak(self, peak: int) -> bool:
        '''
        Check if the manual peak is valid and if so add it to the peaks.
        '''
        if not (peak not in self.peaks and 
            peak not in self.manual_peaks and
              peak >= 0 and peak < len(self.time)):
            return False
        self.manual_peaks.append(peak)
        self.peaks = self.automatic_peaks + self.manual_peaks
        return True

    def non_max_supression(self, threshold: float) -> list[int]:
        '''
        Keeps only maximum peak per threshold crossing.
        '''
        nms_peaks = []
        for i,peak in enumerate(self.automatic_peaks):
            if peak in nms_peaks: continue
            peak_height = self.intensity[peak]
            i_inner = i
            keep = True
            while True:
                if self.intensity[i_inner] < threshold:
                    break
                if self.intensity[i_inner] > peak_height:
                    keep = False
                    break
                if i_inner in self.automatic_peaks:
                    nms_peaks.append(i_inner)
            if not keep:
                nms_peaks.append(peak)
        return nms_peaks

def compute_threshold(stim_used: bool,
                      vals: np.ndarray,
                      threshold_mult: float,
                      threshold_start: int = 0,
                      threshold_stop: int = 50) -> float:
    '''
    Function that computes the threshold above which a peak is considered spike
    based on the formular threshold = mean + std * mult
    '''
    if stim_used  > 0:
        std_ = np.std(vals[threshold_start:threshold_stop])
        mean_ = np.mean(vals[threshold_start:threshold_stop])
        return mean_ + threshold_mult * std_
    std_ = np.std(vals)
    median_ = np.median(vals)
    return median_ + threshold_mult * std_


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
        if len(self.settings_.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings_.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []
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


def paired_pulse_ratio(peaks: pd.DataFrame,
                       stimulation_timepoints: list[int],
                       patience: int) -> pd.DataFrame:
    result = []
    for roi in peaks["ROI#"].unique():
        roi_response = []
        response_for_each_pulse = True
        first_pulse_response = np.nan
        for i,stimulation in enumerate(stimulation_timepoints):
            if peaks[(peaks['Frame'] >= stimulation) &
                     (peaks['Frame'] <= stimulation+patience) &
                     (peaks['ROI#'] == roi)].shape[0] == 0:
                response_for_each_pulse = False
                roi_response.append([f'Pulse {i+1}', roi, np.nan, np.nan, np.nan])
                continue
            max_response_rel = peaks[(peaks['Frame'] >= stimulation) &
                                     (peaks['Frame'] <= stimulation+patience) &
                                     (peaks['ROI#'] == roi)]['rel. Amplitude'].max()
            max_response_abs = peaks[(peaks['Frame'] >= stimulation) &
                                     (peaks['Frame'] <= stimulation+patience) &
                                     (peaks['ROI#'] == roi)]['abs. Amplitude'].max()
            if np.isnan(first_pulse_response):
                first_pulse_response = max_response_abs
            ppr_tmp = max_response_abs/first_pulse_response
            roi_response.append([f'Pulse {i+1}', roi, max_response_rel, max_response_abs, ppr_tmp])
        for i in range(len(roi_response)):
            roi_response[i].append(response_for_each_pulse)
        result += roi_response
    return pd.DataFrame(result,columns=['Pulse', 'ROI', 'rel. Amplitute', 'max. Amplitute', 'PPR', 'responded to all pulses'])
        


class trace_plot:
    def __init__(self, 
                 time: np.ndarray,
                 intenstity: np.ndarray,
                 threshold: float):
        self.time = time
        self.intenstity = intenstity
        self.threshold = threshold

    def create_plot(self) -> None:
        '''
        Creates the basic trace plot with a threshold.
        '''
        self.fig = px.line(x=self.time, y=self.intenstity)
        self.fig.add_hline(y=self.threshold,line_color='red',line_dash='dash')
        self.fig.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                               type="linear"))

    def add_stimulation_window(self,
                               frames: list[int],
                               patience: int) -> None:
        '''
        Adds the stimulation window in yellow after each stimulation for the time
        the user selected in patience.
        '''
        for frame in frames:
            self.fig.add_vrect(x0=frame,
                               x1=frame+patience,
                               fillcolor="yellow",
                               opacity=0.25,
                               line_width=0)
    
    def add_peaks(self,
                  peaks: list,
                  use_nms: bool,
                  selection: list[bool]) -> list:
        '''
        Adds all peaks for selection to the plot.
        '''
        labels = []
        if use_nms:
            peaks = [peak for i,peak in enumerate(peaks) if selection[i]]
        for peak in peaks:
            self.fig.add_annotation(
                x=peak,
                y=self.intenstity[peak],
                text=f'frame: {peak}, height: {self.intenstity[peak]}',
                showarrow=True)
            labels.append(peak)
        return labels
    
    def add_label(self,
                  peak) -> None:
        self.fig.add_annotation(x=peak,
                                y=self.intenstity[peak],
                                text=f'frame: {peak}, height: {self.intenstity[peak]}',
                                showarrow=True)
    
    def reload_plot(self) -> None:
        self.fig.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                                type="linear"))

def peak_detection_scipy(intenstiy: np.ndarray,
                         threshold: float,
                         stim_used: bool,
                         stim_frames: list[int],
                         patience: int) -> list[int]:
    '''
    Peak detection using scipy.
    '''
    peaks = []
    if stim_used and len(stim_frames) > 0:
        for frame in stim_frames:
            tmp_peaks,_ = find_peaks(intenstiy[frame-1:frame+patience+1],height=threshold)
            peaks += [peak+frame-1 for peak in tmp_peaks]
    else:
        tmp_peaks,_ = find_peaks(intenstiy,height=threshold)
        peaks += list(tmp_peaks)
    # specifically for stimulation used it might happen that peaks are detected
    # twice, when the patience window is higher than the time between two 
    # consecutive pulses
    peaks = sorted(list(set(peaks)))
    return peaks


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
        self.w = SettingsWindow(self.settings_,self)
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
        self.synapse_response.keep(self.settings_.config["select_responses"], selection)
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


class gui_settings:
    def __init__(self) -> None:
        self.parse_settings()
    
    def parse_settings(self):
        '''
        Parses the config file from a json file. If the programm is run for the
        first time, the default "default_config.json" file is used, otherwise the
        settings from the previous run are loaded.
        '''
        # ------------------------- user path specific for OS ------------------------ #
        if platform.system() == 'Windows':
            self.config_folder = os.path.join(os.environ.get('USERPROFILE'),'.synapse')
            self.user_config_path = os.path.join(self.config_folder,'config.json')
        else:
            self.config_folder = os.path.join(os.environ.get('HOME'),'.synapse')
            self.user_config_path = os.path.join(self.config_folder,'config.json')
        # -------------------------------- parse file -------------------------------- #
        if os.path.exists(self.user_config_path) and os.path.isfile(self.user_config_path):
            config_path = self.user_config_path
        else:
            config_path = 'default_config.json'
        with open(config_path, 'r') as in_json:
            self.config = json.load(in_json)
    
    def write_settings(self) -> None:
        if not os.path.exists(self.config_folder):
            os.mkdir(self.config_folder)
        with open(self.user_config_path,'w') as out_json:
            json.dump(self.config, out_json)
    
    def get_output_folder(self,parent) -> None:
        self.config['output_folder'] = str(QFileDialog.getExistingDirectory(parent, "Select output directory"))
        self.config['keep_folder'] = os.path.join(self.config['output_folder'],'keep_folder')
        self.config['trash_folder'] = os.path.join(self.config['output_folder'],'trash_folder')
        if not os.path.exists(self.config['keep_folder']):
            os.mkdir(self.config['keep_folder'] )
        if not os.path.exists(self.config['trash_folder']):
            os.mkdir(self.config['trash_folder'])



def main():
    settings = gui_settings()
    app = QApplication(sys.argv)
    main = ui_window(settings)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

