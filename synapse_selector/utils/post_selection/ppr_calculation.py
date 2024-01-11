import pandas as pd
import numpy as np


def paired_pulse_ratio(
    peaks: pd.DataFrame, stimulation_timepoints: list[int], patience: int
) -> pd.DataFrame:
    result = []
    for roi in peaks["ROI#"].unique():
        roi_response = []
        response_for_each_pulse = True
        first_pulse_response = np.nan
        for i, stimulation in enumerate(stimulation_timepoints):
            if (
                peaks[
                    (peaks["Frame"] >= stimulation)
                    & (peaks["Frame"] <= stimulation + patience)
                    & (peaks["ROI#"] == roi)
                ].shape[0]
                == 0
            ):
                response_for_each_pulse = False
                roi_response.append([f"Pulse {i+1}", roi, np.nan, np.nan, np.nan])
                continue
            max_response_rel = peaks[
                (peaks["Frame"] >= stimulation)
                & (peaks["Frame"] <= stimulation + patience)
                & (peaks["ROI#"] == roi)
            ]["rel. Amplitude"].max()
            max_response_abs = peaks[
                (peaks["Frame"] >= stimulation)
                & (peaks["Frame"] <= stimulation + patience)
                & (peaks["ROI#"] == roi)
            ]["abs. Amplitude"].max()
            if np.isnan(first_pulse_response):
                first_pulse_response = max_response_abs
            ppr_tmp = max_response_abs / first_pulse_response
            roi_response.append(
                [f"Pulse {i+1}", roi, max_response_rel, max_response_abs, ppr_tmp]
            )
        for i in range(len(roi_response)):
            roi_response[i].append(response_for_each_pulse)
        result += roi_response
    return pd.DataFrame(
        result,
        columns=[
            "Pulse",
            "ROI",
            "rel. Amplitute",
            "max. Amplitute",
            "PPR",
            "responded to all pulses",
        ],
    )
