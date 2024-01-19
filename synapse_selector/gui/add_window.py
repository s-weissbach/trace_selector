from PyQt6.QtWidgets import (
    QMainWindow,
    QCheckBox,
    QLabel,
    QSpinBox,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from functools import partial
import numpy as np


class AddWindow(QMainWindow):
    def __init__(
        self,
        add_handler,
        close_handler,
        parent=None,
        maximum_length=0,
        preds=[],
        intensities=[],
    ):
        super().__init__(parent)

        # variables
        self.parent = parent
        self.add_handler = add_handler
        self.close_handler = close_handler
        self.peak_dict = {}
        self.peak_widgets = []
        self.preds = preds
        self.intensities = intensities

        self.setWindowTitle("Edit responses")

        main_wrapper_widget = QWidget()
        main_layout = QVBoxLayout()
        main_wrapper_widget.setLayout(main_layout)

        self.setCentralWidget(main_wrapper_widget)

        desc_label = QLabel(
            "Insert the x-coordinate of the response using the input box or the range slider:"
        )
        main_layout.addWidget(desc_label)

        self.spinner_input = QSpinBox()
        self.spinner_input.setMinimum(0)
        self.spinner_input.setMaximum(maximum_length)
        self.spinner_input.setSingleStep(1)
        self.spinner_input.valueChanged.connect(self.__update_input)
        self.spinner_input.setValue(0)
        main_layout.addWidget(self.spinner_input)

        self.slider_input = QSlider(Qt.Orientation.Horizontal)
        self.slider_input.setMinimum(0)
        self.slider_input.setMaximum(maximum_length)
        self.slider_input.setSingleStep(1)
        self.slider_input.valueChanged.connect(self.__update_input)
        self.slider_input.setValue(0)
        main_layout.addWidget(self.slider_input)

        button_wrapper_widget = QWidget()
        button_layout = QHBoxLayout()
        button_wrapper_widget.setLayout(button_layout)
        main_layout.addWidget(button_wrapper_widget)

        self.add_button = QPushButton("Add Response")
        button_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.__add_trace)

        close_button = QPushButton("Close")
        close_button.clicked.connect(close_handler)
        button_layout.addWidget(close_button)

        scroll = QScrollArea()

        self.peak_widget_layout = QVBoxLayout()
        self.peak_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.peak_widget_layout.setSpacing(0)
        peak_widget_wrapper_widget = QWidget()
        peak_widget_wrapper_widget.setLayout(self.peak_widget_layout)

        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(peak_widget_wrapper_widget)

        main_layout.addWidget(scroll)

    def __update_button_text(self):
        val = self.get_input()
        if self.parent.settings.config["peak_detection_type"] != "Thresholding":
            self.add_button.setText(
                f"Add Response (Int.: {np.round(self.intensities[val], 2)} | Conf.: {np.round(self.preds[val] * 100, 2)})"
            )
        else:
            self.add_button.setText(
                f"Add Response (Int.: {np.round(self.intensities[val], 2)})"
            )

    def __add_trace(self):
        # value is already a peak, just return
        if self.get_input() in list(self.peak_dict.keys()):
            return
        # get input and append it
        peak_value = self.get_input()
        self.add_handler(peak_value)
        self.peak_dict[peak_value] = (True, True)
        # use the previous length as the index for the current element
        self.__add_peak_widget(peak_value)
        self.__reset_input()

    def __add_peak_widget(self, peak_value: int):
        # create layout
        widget_layout = QHBoxLayout()
        widget_layout_wrapper = QWidget()
        widget_layout_wrapper.setLayout(widget_layout)
        # create widgets
        if self.parent.settings.config["peak_detection_type"] != "Thresholding":
            label = QLabel(
                f"[Frame: {peak_value} | Int.: {np.round(self.intensities[peak_value], 2)} | Conf.: {np.round(self.preds[peak_value] * 100, 2)}]"
            )
        else:
            label = QLabel(
                f"[Frame: {peak_value} | Int.: {np.round(self.intensities[peak_value], 2)}"
            )
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(
            partial(self.__toggle_peak, peak_value=peak_value)
        )

        checkbox.setChecked(self.peak_dict[peak_value][0])

        widget_layout.addWidget(checkbox)
        widget_layout.addWidget(label)
        widget_layout.addStretch()

        self.peak_widget_layout.addWidget(widget_layout_wrapper)
        # append widget to list
        self.peak_widgets.append(widget_layout_wrapper)

    def __update_input(self, value):
        self.slider_input.setValue(value)
        self.spinner_input.setValue(value)
        self.__update_button_text()

    def __toggle_peak(self, new_state, peak_value):
        # 2: checked | 0: unchecked
        self.peak_dict[peak_value] = (
            True if new_state == 2 else False,
            self.peak_dict[peak_value][1],
        )
        # if nms is activated, reload the plot
        if self.parent.get_setting("nms"):
            self.parent.plot()

    def get_selected_peaks(self):
        peaks = []
        for peak, bools in self.peak_dict.items():
            if bools[0]:
                peaks.append(peak)
        return peaks

    def get_peak_dict(self):
        return_dict = {}
        for key, item in self.peak_dict.items():
            return_dict[key] = item[0]
        return return_dict

    def get_input(self):
        return self.spinner_input.value()

    def __reset_input(self):
        self.spinner_input.setValue(0)
        self.slider_input.setValue(0)

    def reset(self):
        self.reset_peak_widgets()
        self.__reset_input()
        self.peak_dict = {}

    def reset_peak_widgets(self):
        for peak_widget in self.peak_widgets:
            self.peak_widget_layout.removeWidget(peak_widget)
            peak_widget.deleteLater()
            peak_widget = None
        self.peak_widgets = []

    def update_length(self, value):
        self.spinner_input.setMaximum(value)
        self.slider_input.setMaximum(value)
        self.__reset_input()

    def update_information(self, pred_arr, intensity_arr):
        self.preds = pred_arr
        self.intensities = intensity_arr

    def load_peaks(self, peak_arr):
        tmp_peak_dict = self.peak_dict.copy()
        self.reset()
        for idx, peak in enumerate(peak_arr):
            self.peak_dict[peak] = (True, False)
            self.__add_peak_widget(peak)
        for peak, bool_arr in tmp_peak_dict.items():
            # peak was manually added
            if bool_arr[1]:
                self.peak_dict[peak] = (True, False)
