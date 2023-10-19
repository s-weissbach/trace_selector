import numpy as np
import plotly.express as px


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
        self.fig.add_hline(y=self.threshold, line_color='red', line_dash='dash')
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
            peaks = [peak for i, peak in enumerate(peaks) if selection[i]]
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
