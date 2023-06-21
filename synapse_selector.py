import os
import sys

import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from PyQt6 import QtWebEngineWidgets
from PyQt6.QtCore import Qt#, QRegExp
from PyQt6.QtWidgets import (QApplication, QLabel, QSpinBox, QFileDialog,
                             QHBoxLayout, QMessageBox, QCheckBox, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget, QDoubleSpinBox,
                             QVBoxLayout)
from PyQt6.QtGui import QFont#, QRegExpValidator
from scipy.signal import find_peaks

home = os.getenv("HOME")


class ui_window(QWidget):
    def __init__(self):
        super().__init__()
        self.directory = None
        
        # layout
        self.mainwindowlayout = QVBoxLayout()
        self.current_file_label = QLabel('')
        self.mainwindowlayout.addWidget(self.current_file_label)
        self.current_state_indicator = QLabel('')
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.current_state_indicator.setFont(font)
        self.mainwindowlayout.addWidget(self.current_state_indicator)
        self.trace_plot = QtWebEngineWidgets.QWebEngineView(self)
        self.trace_plot.setMinimumSize(1500, 500)
        self.mainwindowlayout.addWidget(self.trace_plot)
        # buttons
        self.buttonlayout = QHBoxLayout()
        # back
        self.back_button = QPushButton('back')
        self.back_button.clicked.connect(self.back)
        self.buttonlayout.addWidget(self.back_button)
        # threshold start and stop
        self.threshold_start_desc = QLabel('Baseline start:')
        self.threshold_start_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.buttonlayout.addWidget(self.threshold_start_desc)
        self.threshold_start_input = QSpinBox()
        self.threshold_start_input.setValue(0)
        self.buttonlayout.addWidget(self.threshold_start_input)
        self.threshold_stop_desc = QLabel('Baseline stop:')
        self.threshold_stop_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.buttonlayout.addWidget(self.threshold_stop_desc)
        self.threshold_stop_input = QSpinBox()
        self.threshold_stop_input.setValue(70)
        
        self.buttonlayout.addWidget(self.threshold_stop_input)
        # threshold multiplier
        self.threshold_desc = QLabel('Threshold multiplier:')
        self.threshold_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.buttonlayout.addWidget(self.threshold_desc)
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setSingleStep(0.1)
        self.threshold_input.setValue(4)
        self.threshold_input.valueChanged.connect(self.plot)
        self.buttonlayout.addWidget(self.threshold_input)
        # stimulation used
        self.stim_used_box = QCheckBox('Stimulation used')
        self.stim_used_box.setChecked(True)
        self.stim_used = True
        self.stim_used_box.stateChanged.connect(self.toggle_stim_used)
        self.buttonlayout.addWidget(self.stim_used_box)
        # xlsx export
        self.xlsx_export_box = QCheckBox('Export as .xlsx')
        self.xlsx_export_box.setChecked(False)
        self.buttonlayout.addWidget(self.xlsx_export_box)
        # trash
        self.trash_button = QPushButton('trash')
        self.trash_button.clicked.connect(self.trash_trace)
        self.buttonlayout.addWidget(self.trash_button)
        # keep
        self.keep_button = QPushButton('keep')
        self.keep_button.clicked.connect(self.keep_trace)
        self.buttonlayout.addWidget(self.keep_button)
        self.mainwindowlayout.addLayout(self.buttonlayout)
        # --------------------- second layer for spike selection --------------------- #
        self.response_layout = QHBoxLayout()
        self.activate_response_selection = QCheckBox('Select Responses')
        self.activate_response_selection.setChecked(False)
        self.activate_response_selection.stateChanged.connect(self.toggle_response_selection)
        self.response_layout.addWidget(self.activate_response_selection)
        # stim frames
        self.stimframes_label = QLabel('Stimulation Frames')
        self.response_layout.addWidget(self.stimframes_label)
        self.stimframes_input = QLineEdit('50,60')
        # Define the regular expression pattern
        pattern = "^(\d+,)*(\d+)?$"
        #regexp = QRegExp(pattern)
        # Create a validator using the regular expression
        #validator = QRegExpValidator(regexp)
        # Set the validator for your QLineEdit
        #self.stimframes_input.setValidator(validator)
        self.stimframes_input.setMaximumWidth(200)
        self.stimframes_input.setEnabled(False)
        self.stimframes_input.editingFinished.connect(self.toggle_response_selection)
        self.response_layout.addWidget(self.stimframes_input)
        self.patience_label = QLabel('Patience')
        self.response_layout.addWidget(self.patience_label)
        self.patience_input = QSpinBox()
        self.patience_input.setValue(10)
        self.patience_input.setEnabled(False)
        self.response_layout.addWidget(self.patience_input)
        # nms toggle
        self.non_max_supression_button = QCheckBox('Non-Maximum Supression')
        self.non_max_supression_button.setChecked(False)
        self.use_nms = False
        self.non_max_supression_button.stateChanged.connect(self.nms_toggle)
        self.response_layout.addWidget(self.non_max_supression_button)
        
        self.response_layout.addStretch()
        self.mainwindowlayout.addLayout(self.response_layout)
        # selection box layout
        self.response_selection_layout = QHBoxLayout()
        self.response_input_label = QLabel('Add Response: ')
        self.response_selection_layout.addWidget(self.response_input_label)
        self.response_input = QLineEdit()
        self.response_input.setMaximumWidth(200)
        #regex2 = QRegExp("[0-9]*")
        #validator2 = QRegExpValidator(regex2)
        #self.response_input.setValidator(validator2)
        self.response_input.returnPressed.connect(self.add_response)
        self.response_selection_layout.addWidget(self.response_input)
        self.response_input.setEnabled(False)
        self.response_selection_layout.addStretch()
        self.mainwindowlayout.addLayout(self.response_selection_layout)
        # --------------------------- dynamic button layout -------------------------- #
        self.response_button_v_layout = QVBoxLayout()
        self.response_button_layout_list = [QHBoxLayout()]
        self.response_button_list = []
        self.response_button_v_layout.addLayout(self.response_button_layout_list[0])
        self.mainwindowlayout.addLayout(self.response_button_v_layout)
        # ------------------------------ start programm ------------------------------ #
        self.setLayout(self.mainwindowlayout)
        # output directory
        self.get_output_folder()
        # select file
        self.get_filepath()
        # load file
        self.open_file()
        # plot
        self.plot()
        # link buttons to plot function
        self.threshold_input.valueChanged.connect(self.plot)
        self.threshold_stop_input.valueChanged.connect(self.plot)
        self.threshold_start_input.valueChanged.connect(self.plot)
        self.patience_input.valueChanged.connect(self.toggle_response_selection)
        self.selected_peaks = []

    def get_output_folder(self):
        self.output_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.keep_folder = os.path.join(self.output_folder,'keep_folder')
        self.trash_folder = os.path.join(self.output_folder,'trash_folder')
        if not os.path.exists(self.keep_folder):
            os.mkdir(self.keep_folder)
        if not os.path.exists(self.trash_folder):
            os.mkdir(self.trash_folder)
     
    def get_filepath(self):
        if self.directory is not None:
            self.filepath = QFileDialog.getOpenFileName(
                caption='Select Input File',
                directory=self.directory,
                filter="Table(*.txt *.csv *.xlsx *.xls)",)[0]
        else:
            self.filepath = QFileDialog.getOpenFileName(
                caption='Select Input File',
                filter="Table(*.txt *.csv *.xlsx *.xls)",)[0]
        if self.filepath == "":
            # question(parent: QWidget, title: str, text: str, buttons: QMessageBox.StandardButton = QMessageBox.StandardButtons(QMessageBox.Yes|QMessageBox.No), defaultButton: QMessageBox.StandardButton = QMessageBox.NoButton)
            response = QMessageBox.question(self, 'No file selected', "Do you wish to terminate the programm?")
            #response.setStandardButtons()
            print(1)
            print(response)

            if response == QMessageBox.StandardButton.No :
                self.get_filepath()
            else:
                sys.exit()
        self.current_keep_folder = os.path.join(self.keep_folder,os.path.basename(self.filepath))
        if not os.path.exists(self.current_keep_folder):
            os.mkdir(self.current_keep_folder)
        self.current_trash_folder = os.path.join(self.trash_folder,os.path.basename(self.filepath))
        if not os.path.exists(self.current_trash_folder):
            os.mkdir(self.current_trash_folder)
        self.filename = os.path.basename(self.filepath)
        self.directory = os.path.dirname(self.filepath)
        self.current_file_label.setText(self.filepath)

    def open_file(self):
        if self.filepath.endswith('.txt') or self.filepath.endswith('.csv'):
            self.synapse_response_df = pd.read_csv(self.filepath,sep=',')
        else:
            self.synapse_response_df = pd.read_excel(self.filepath)
        self.meta_columns = ["file name","total frames","macro version","xSD ROI","xSD Z","ROI radius","frames baseline","frames response","abs frame #","rel frame #","empty","average Z"]
        self.meta_columns = [col for col in self.meta_columns if col in self.synapse_response_df.columns]
        self.columns = [col for col in self.synapse_response_df.columns if col not in self.meta_columns]
        self.idx = 0
        self.keep_data = []
        self.trash_data = []
        self.last = []
        self.peaks = []
        self.manual_peaks = []
        self.peak_selection_buttons = []
        self.threshold_start_input.setMaximum(self.synapse_response_df.shape[0])
        self.threshold_stop_input.setMaximum(self.synapse_response_df.shape[0])
        self.labels = []
    
    def plot(self):
        self.y = self.synapse_response_df[self.columns[self.idx]].to_list()
        x = np.arange(len(self.y))
        if self.stim_used and self.threshold_stop_input.value() > 0:
            std_ = np.std(self.y[self.threshold_start_input.value():self.threshold_stop_input.value()])
            mean_ = np.mean(self.y[self.threshold_start_input.value():self.threshold_stop_input.value()])
            self.threshold = mean_ + self.threshold_input.value() * std_
        else:
            std_ = np.std(self.y)
            mean_ = np.median(self.y)
            self.threshold = mean_ + self.threshold_input.value() * std_
        # 

        self.fig = px.line(x=x, y=self.y)
        self.fig.add_hline(y=self.threshold,line_color='red',line_dash='dash')
        
        if self.activate_response_selection.isChecked():
            if self.stim_used:
                for frame in self.stimframes:
                    self.fig.add_vrect(x0=frame, x1=frame+self.patience, 
                        fillcolor="yellow", opacity=0.25, line_width=0)
            self.peak_selection()
            for i,peak in enumerate(self.peaks):
                if self.use_nms:
                    if self.peak_selection_buttons[i].isChecked():
                        self.labels.append(peak)
                        self.fig.add_annotation(x=peak,y=self.y[peak],text=f'frame: {peak}, height: {self.y[peak]}', showarrow=True)
                else:
                    self.fig.add_annotation(x=peak,y=self.y[peak],text=f'frame: {peak}, height: {self.y[peak]}', showarrow=True)
        self.fig.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"))
        self.trace_plot.setHtml(
            self.fig.to_html(include_plotlyjs="cdn")
            
        )
        self.current_state_indicator.setText(f'{self.idx+1}/{len(self.columns)}')
    
    def back(self):
        if self.idx == 0:
            return
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
        self.next()

    def keep_trace(self):
        self.keep_data.append(self.columns[self.idx])
        self.last.append('keep')
        if self.activate_response_selection.isChecked():
            for button in self.peak_selection_buttons:
                if not button.isChecked():
                    continue
                peak_tp = int(button.text().split(" ")[1])
                amplitude = self.y[peak_tp]
                baseline = np.min(self.y[max(0,peak_tp-15):peak_tp])
                relative_height = amplitude-baseline
                relative_height50 = relative_height/2 + baseline
                tmp = np.where(self.y[peak_tp:]<relative_height50)[0]
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
        self.next()

    def trash_trace(self):
        self.trash_data.append(self.columns[self.idx])
        self.last.append('trash')
        self.next()

    def next(self):
        self.labels = []
        self.idx += 1
        if len(self.columns) == self.idx:
            for button in self.peak_selection_buttons:
                self.response_selection_layout.removeWidget(button)
                button.deleteLater()
                button = None
            self.save()
            self.get_filepath()
            self.open_file()
        self.peaks = []
        self.manual_peaks = []
        for button in self.peak_selection_buttons:
                self.response_selection_layout.removeWidget(button)
                button.deleteLater()
                button = None
        self.peak_selection_buttons = []
        self.plot()
    
    def save(self):
        keep_df = self.synapse_response_df[self.meta_columns+self.keep_data]
        trash_df = self.synapse_response_df[self.meta_columns+self.trash_data]
        if self.xlsx_export_box.isChecked():
            keep_df.to_excel(os.path.join(self.current_keep_folder,f'{self.filename}.xlsx'),index=False)
            trash_df.to_excel(os.path.join(self.current_trash_folder,f'{self.filename}.xlsx'),index=False)
        elif self.filename.endswith('.xlsx') or self.filename.endwith('.xls'):
            keep_df.to_excel(os.path.join(self.current_keep_folder,f'{self.filename}.xlsx'),index=False)
            trash_df.to_excel(os.path.join(self.current_trash_folder,f'{self.filename}.xlsx'),index=False)
        else:
        	keep_df.to_csv(os.path.join(self.current_keep_folder,self.filename),index=False)
        	trash_df.to_csv(os.path.join(self.current_trash_folder,self.filename),index=False)
        if len(self.selected_peaks) > 0:
            output_name = f"{'.'.join(self.filename.split('.')[:-1])}_responses.csv"
            peak_df = pd.DataFrame(self.selected_peaks,columns=['Filename','ROI#','Frame','abs. Amplitude', 'rel. Amplitude','decay50'])
            peak_df.to_csv(os.path.join(self.current_keep_folder,output_name),index=False)
            
    def toggle_response_selection(self):
        if self.activate_response_selection.isChecked():
            if self.stim_used_box.isChecked():
                self.stimframes_input.setEnabled(True)
                self.patience_input.setEnabled(True)
            self.response_input.setEnabled(True)
            self.patience = self.patience_input.value()
            if len(self.stimframes_input.text()) > 0:
                self.stimframes = [int(frame) for frame in self.stimframes_input.text().split(',')]
            else:
                self.stimframes = []
            self.peak_detection()
        else:
            for button in self.peak_selection_buttons:
                self.response_selection_layout.removeWidget(button)
                button.deleteLater()
                button = None
            self.peaks = []
            self.peak_selection_buttons = []
            self.stimframes_input.setEnabled(False)
            self.patience_input.setEnabled(False)
            self.response_input.setEnabled(False)
            self.labels = []
        self.plot()
    
    def add_response(self):
        peak = int(self.response_input.text())
        if peak not in self.peaks and peak not in self.manual_peaks and peak >= 0 and peak < len(self.y):
            self.manual_peaks.append(peak)
        else:
            return
        self.peaks = self.automatic_peaks + self.manual_peaks
        # add label
        if self.current_layout_count > 14:
            self.current_layout_count = 0
            self.current_layout_row += 1
            # if needed add new layout
            if len(self.response_button_layout_list)-1 <= self.current_layout_row:
                self.response_button_layout_list.append(QHBoxLayout())
                self.response_button_v_layout.addLayout(self.response_button_layout_list[-1])
        self.peak_selection_buttons.append(QCheckBox(f'Peak {peak}'))
        self.peak_selection_buttons[-1].setChecked(True)
        self.response_button_layout_list[self.current_layout_row].addWidget(self.peak_selection_buttons[-1])
        self.current_layout_count += 1
        # add response to plot
        self.label_changed()
        # empty QLineEdit
        self.response_input.setText('')

    def peak_detection(self):
        self.peaks = []
        if self.stim_used and len(self.stimframes) > 0:
            for frame in self.stimframes:
                tmp_peaks,_ = find_peaks(self.y[frame:frame+self.patience],height=self.threshold)
                self.peaks += [peak+frame for peak in tmp_peaks]
        else:
            tmp_peaks,_ = find_peaks(self.y,height=self.threshold)
            self.peaks += list(tmp_peaks)
        self.automatic_peaks = self.peaks.copy()
        self.peaks += self.manual_peaks

    def peak_selection(self):
        self.peak_detection()
        for button in self.peak_selection_buttons:
            self.response_selection_layout.removeWidget(button)
            button.deleteLater()
            button = None
        self.peak_selection_buttons = []
        # have 10 buttons per layout
        self.current_layout_count = 0
        self.current_layout_row = 0
        for i,peak in enumerate(self.peaks):
            if self.current_layout_count > 14:
                self.current_layout_count = 0
                self.current_layout_row += 1
                # if needed add new layout
                if len(self.response_button_layout_list)-1 <= self.current_layout_row:
                    self.response_button_layout_list.append(QHBoxLayout())
                    self.response_button_v_layout.addLayout(self.response_button_layout_list[-1])
            self.peak_selection_buttons.append(QCheckBox(f'Peak {peak}'))
            self.response_button_layout_list[self.current_layout_row].addWidget(self.peak_selection_buttons[-1])
            if peak in self.manual_peaks:
                self.peak_selection_buttons[-1].setChecked(True)
            elif i>0 and self.y[self.peaks[i-1]] > self.y[self.peaks[i]] and self.peaks[i-1]-self.peaks[i] < 5 and self.use_nms:
                self.peak_selection_buttons[-1].setChecked(False)
            else:
                self.peak_selection_buttons[-1].setChecked(True)
            self.current_layout_count += 1
        for button in self.peak_selection_buttons:
            button.stateChanged.connect(self.label_changed)
    
    def toggle_stim_used(self):
        if self.stim_used_box.isChecked() and self.activate_response_selection.isChecked():
            self.stim_used = True
            self.threshold_start_input.setEnabled(True)
            self.threshold_stop_input.setEnabled(True)
            self.stimframes_input.setEnabled(True)
            self.patience_input.setEnabled(True)
            self.peak_selection()
        else:
            self.stimframes_input.setEnabled(False)
            self.threshold_start_input.setEnabled(False)
            self.threshold_stop_input.setEnabled(False)
            self.patience_input.setEnabled(False)
            self.stim_used = False
        self.plot()
    
    def label_changed(self) -> None:
        change_made = False
        for i,peak in enumerate(self.peaks):
            if peak in self.labels: continue
            if self.peak_selection_buttons[i].isChecked():
                change_made = True
                self.labels.append(peak)
                self.fig.add_annotation(x=peak,y=self.y[peak],text=f'frame: {peak}, height: {self.y[peak]}', showarrow=True)
        if change_made:
            self.fig.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                                type="linear"))
            self.trace_plot.setHtml(
                self.fig.to_html(include_plotlyjs="cdn"))
    
    def nms_toggle(self) -> None:
        if self.non_max_supression_button.isChecked():
            self.use_nms = True
        else:
            self.use_nms = False
        self.plot()
    

def main():
    app = QApplication(sys.argv)
    main = ui_window()
    main.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
