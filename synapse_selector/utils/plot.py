import numpy as np
import plotly.express as px

import plotly.graph_objects as go
import pandas as pd
from typing import Union


class trace_plot:
    def __init__(
        self,
        time: np.ndarray,
        intenstity: np.ndarray,
        threshold: float,
        probabilities=[],
    ):
        self.time = time
        self.intenstity = intenstity
        self.threshold = threshold
        if len(probabilities) == 0:
            self.probabilities = [0 for _ in range(len(time))]
        else:
            self.probabilities = [f"{np.round(p*100,2)}%" for p in probabilities]
        self.plot_df = pd.DataFrame(
            {
                "Time": self.time,
                "Intensity": self.intenstity,
                "Probability": self.probabilities,
            }
        )

    def create_plot(self, v_line_value=None) -> None:
        """
        Creates the basic trace plot with a threshold.
        """
        self.fig = px.line(
            self.plot_df, x="Time", y="Intensity", hover_data="Probability"
        )
        self.fig.update_layout(
            template="plotly_white",
            xaxis=dict(rangeslider=dict(visible=True), type="linear"),
        )
        self.fig.add_hline(y=self.threshold, line_color="red", line_dash="dash")
        width = 0 if v_line_value == 0 else 2
        min_val = min(self.intenstity) - 0.1 * min(self.intenstity)
        max_val = max(self.intenstity) - 0.1 * max(self.intenstity)
        self.v_line = go.Scatter(
            x=[v_line_value, v_line_value],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="orange", width=width),
            hoverinfo="none",
            showlegend=False,
        )
        self.fig.add_trace(self.v_line)

    def add_stimulation_window(self, frames: list[int], patience: int) -> None:
        """
        Adds the stimulation window in yellow after each stimulation for the time
        the user selected in patience.
        """
        for frame in frames:
            self.fig.add_vrect(
                x0=frame,
                x1=frame + patience,
                fillcolor="yellow",
                opacity=0.25,
                line_width=0,
            )

    def add_peaks(
        self,
        peaks: list,
        use_nms: bool,
        selection: list[bool],
        probabilities: Union[list[float], np.ndarray] = [],
    ) -> list:
        """
        Adds all peaks for selection to the plot.
        """
        labels = []
        if use_nms:
            peaks = [peak for i, peak in enumerate(peaks) if selection[i]]
        for peak in peaks:
            if len(probabilities) > 0:
                self.fig.add_annotation(
                    x=peak,
                    y=self.intenstity[peak],
                    text=f"frame: {peak}, height: {np.round(self.intenstity[peak],2)}, probability: {np.round(probabilities[peak]*100,2)}%",
                    showarrow=True,
                )
            else:
                self.fig.add_annotation(
                    x=peak,
                    y=self.intenstity[peak],
                    text=f"frame: {peak}, height: {self.intenstity[peak]}",
                    showarrow=True,
                )
            labels.append(peak)
        return labels

    def add_label(self, peak) -> None:
        self.fig.add_annotation(
            x=peak,
            y=self.intenstity[peak],
            text=f"frame: {peak}, height: {self.intenstity[peak]}",
            showarrow=True,
        )

    def reload_plot(self) -> None:
        self.fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True), type="linear")
        )
