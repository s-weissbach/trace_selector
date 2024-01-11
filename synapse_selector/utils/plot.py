import numpy as np
import plotly.express as px
import pandas as pd
from typing import Union


class trace_plot:
    def __init__(
        self,
        time: np.ndarray,
        intensity: np.ndarray,
        threshold: float,
        peak_detection_type="Thresholding",
        probabilities=[],
        always_show_threshold=False,
    ):
        self.time = time
        self.intensity = intensity
        self.threshold = threshold
        self.peak_detection_type = peak_detection_type
        self.always_show_threshold = always_show_threshold

        if len(probabilities) == 0:
            self.probabilities = [0 for _ in range(len(time))]
        else:
            self.probabilities = [f"{np.round(p*100,2)}%" for p in probabilities]
        self.plot_df = pd.DataFrame(
            {
                "Time": self.time,
                "Intensity": self.intensity,
                "Confidence": self.probabilities,
            }
        )

    def create_plot(self) -> None:
        """
        Creates the basic trace plot with a threshold.
        """
        self.fig = px.line(
            self.plot_df, x="Time", y="Intensity", hover_data="Confidence"
        )
        self.fig.update_layout(
            template="plotly_white",
            xaxis=dict(rangeslider=dict(visible=True), type="linear"),
        )

        if self.peak_detection_type == "Thresholding" or self.always_show_threshold:
            self.fig.add_hline(y=self.threshold, line_color="red", line_dash="dash")

    def add_stimulation_window(
        self, frames: list[int], patience: int, start: int = 0, step: int = 30
    ) -> None:
        """
        Adds the stimulation window in yellow after each stimulation for the time
        the user selected in patience.
        """
        # if frames is not empty
        if frames:
            for frame in frames:
                self.fig.add_vrect(
                    x0=frame,
                    x1=frame + patience,
                    fillcolor="yellow",
                    opacity=0.25,
                    line_width=0,
                )
            return
        length = len(self.time)
        print(length)
        num_steps = (length // step) + 1
        print(num_steps)
        steps = np.arange(0, num_steps) * step + start
        print(steps)

        for step in steps:
            self.fig.add_vrect(
                x0=step,
                x1=step + patience if step + patience < length else length - 1,
                fillcolor="yellow",
                opacity=0.25,
                line_width=0,
            )

    def add_peaks(
        self,
        peak_dict: dict[str:bool],
        use_nms: bool,
    ) -> list:
        """Adds all peaks for selection to the plot."""
        res = []
        peaks = [
            peak
            for peak, selected in peak_dict.items()
            if (selected if use_nms else True)
        ]
        for peak in peaks:
            self.add_annotation(peak)
            res.append(peak)
        return res

    def add_annotation(self, peak) -> None:
        if len(self.probabilities) > 0:
            self.fig.add_annotation(
                x=peak,
                y=self.intensity[peak],
                text=f"Frame: {peak} | Int.: {np.round(self.intensity[peak], 2)} | Conf.: {self.probabilities[peak]}",
                showarrow=True,
            )
        else:
            self.fig.add_annotation(
                x=peak,
                y=self.intensity[peak],
                text=f"Frame: {peak} | Int.: {np.round(self.intensity[peak], 2)}",
                showarrow=True,
            )

    def reload_plot(self) -> None:
        self.fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True), type="linear")
        )
