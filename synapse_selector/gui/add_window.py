from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QSpinBox,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
)
from PyQt6.QtCore import Qt


class AddWindow(QMainWindow):
    def __init__(self, add_handler, close_handler, v_line_handler, parent=None, maximum_length=0, preds=[]):
        super().__init__(parent)

        # variables
        self.parent = parent
        self.add_handler = add_handler
        self.close_handler = close_handler
        self.v_line_handler = v_line_handler
        self.peak_array = []
        self.peak_widgets = []
        self.preds = preds

        self.setWindowTitle("Add a peak")

        main_wrapper_widget = QWidget()
        main_layout = QVBoxLayout()
        main_wrapper_widget.setLayout(main_layout)

        self.setCentralWidget(main_wrapper_widget)

        desc_label = QLabel('Insert the x-coordinate of the peak using the input box or the range slider:')
        main_layout.addWidget(desc_label)

        self.spinner_input = QSpinBox()
        self.spinner_input.setMinimum(0)
        self.spinner_input.setMaximum(maximum_length)
        self.spinner_input.setSingleStep(1)
        self.spinner_input.valueChanged.connect(self.__update_input__)
        self.spinner_input.setValue(0)
        main_layout.addWidget(self.spinner_input)

        self.slider_input = QSlider(Qt.Orientation.Horizontal)
        self.slider_input.setMinimum(0)
        self.slider_input.setMaximum(maximum_length)
        self.slider_input.setSingleStep(1)
        self.slider_input.valueChanged.connect(self.__update_input__)
        self.slider_input.setValue(0)
        main_layout.addWidget(self.slider_input)

        button_wrapper_widget = QWidget()
        button_layout = QHBoxLayout()
        button_wrapper_widget.setLayout(button_layout)
        main_layout.addWidget(button_wrapper_widget)

        add_button = QPushButton('Add Trace')
        button_layout.addWidget(add_button)
        add_button.clicked.connect(self.add_trace)

        close_button = QPushButton('Close')
        close_button.clicked.connect(close_handler)
        button_layout.addWidget(close_button)

        main_layout.addStretch()

        self.peak_widget_layout = QVBoxLayout()
        peak_widget_wrapper_widget = QWidget()
        peak_widget_wrapper_widget.setLayout(self.peak_widget_layout)
        main_layout.addWidget(peak_widget_wrapper_widget)

    def add_trace(self):
        # value is already a peak, just return
        if self.get_input() in self.peak_array:
            return
        self.add_handler()
        self.peak_array.append(self.get_input())
        self.add_peak_widget(self.get_input())
        self.reset_input()

    def get_input(self):
        return self.spinner_input.value()

    def reset_input(self):
        self.spinner_input.setValue(0)
        self.slider_input.setValue(0)
        self.v_line_handler(0)

    def __update_input__(self, value):
        self.slider_input.setValue(value)
        self.spinner_input.setValue(value)
        self.v_line_handler(value)

    def update_length(self, value):
        self.spinner_input.setMaximum(value)
        self.slider_input.setMaximum(value)
        self.reset_input()

    def update_preds(self, pred_arr):
        self.preds = pred_arr

    def load_peaks(self, peak_arr):
        for peak_widget in self.peak_widgets:
            self.peak_widget_layout.removeWidget(peak_widget)
            peak_widget.deleteLater()
            peak_widget = None
        self.peak_widgets = []
        self.peak_array = peak_arr
        for peak in self.peak_array:
            self.add_peak_widget(peak)

    def add_peak_widget(self, peak_value):
        label = QLabel(f'[Peak: {peak_value}]')
        self.peak_widget_layout.addWidget(label)
        self.peak_widgets.append(label)
