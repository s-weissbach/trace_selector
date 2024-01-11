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
                stimulation_list.append([filename, roi, np.nan, 0, 0])
                continue
            # abs. Amplitude	rel. Amplitude
            rel_amplitude = -np.inf
            abs_amplitude = -np.inf
            frame = -np.inf
            for _, row in responses_stim.iterrows():
                if row["rel. Amplitude"] < rel_amplitude:
                    continue
                rel_amplitude = row["rel. Amplitude"]
                abs_amplitude = row["abs. Amplitude"]
                frame = row["Frame"]
            stimulation_list.append(
                [filename, roi, frame, abs_amplitude, rel_amplitude]
            )
    stimulation_df = pd.DataFrame(
        stimulation_list,
        columns=["Filename", "ROI#", "Frame", "rel. Amplitude", "abs. Amplitude"],
    )
    return stimulation_df
