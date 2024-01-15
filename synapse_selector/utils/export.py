import pandas as pd
import numpy as np


def create_stimulation_df(
    stimulations: list[int], patience: int, responses: pd.DataFrame
) -> pd.DataFrame:
    stimulation_list = []
    filename = responses.loc[0, "Filename"]
    for roi in responses["ROI#"].unique():
        responses_roi = responses[responses["ROI#"] == roi]
        for stimulation in stimulations:
            responses_stim = responses_roi[
                (responses_roi["Frame"] >= stimulation)
                & (responses_roi["Frame"] <= stimulation + patience)
            ]
            if responses_stim.shape[0] == 0:
                stimulation_list.append([filename, roi, stimulation, np.nan, 0, 0])
                continue
            # abs. Amplitude	rel. Amplitude
            rel_amplitude = -np.inf
            abs_amplitude = -np.inf
            rel_norm_amplitude = -np.inf
            abs_norm_amplitude = -np.inf
            frame = -np.inf
            for _, row in responses_stim.iterrows():
                if row["rel. Amplitude"] < rel_amplitude:
                    continue
                rel_amplitude = row["rel. Amplitude"]
                rel_norm_amplitude = row["rel. norm. Amplitude"]
                abs_amplitude = row["abs. Amplitude"]
                abs_norm_amplitude = row["abs. norm. Amplitude"]
                frame = row["Frame"]
            stimulation_list.append(
                [
                    filename,
                    roi,
                    stimulation,
                    frame,
                    abs_amplitude,
                    rel_amplitude,
                    abs_norm_amplitude,
                    rel_norm_amplitude,
                ]
            )
    stimulation_df = pd.DataFrame(
        stimulation_list,
        columns=[
            "Filename",
            "ROI#",
            "Stimulation Frame",
            "Response Frame",
            "abs. Amplitude",
            "rel. Amplitude",
            "abs. norm. Amplitude",
            "rel. norm. Amplitude",
        ],
    )
    return stimulation_df
