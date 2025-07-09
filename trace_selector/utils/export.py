from typing import Literal
import pandas as pd
import numpy as np
from ..utils.normalization import sliding_window_normalization, baseline_normalization


def normalized_trace_df(
    trace_df: pd.DataFrame,
    normalization_mode: Literal[10,11,12,13], 
    normalization_sliding_window: int,
    normalization_baseline_window: tuple[int,int]
) -> pd.DataFrame:
    norm_trace_df = pd.DataFrame()
    for col in trace_df.columns:
        if normalization_mode == 11 or normalization_mode == 12:
            norm_trace_df[col] = sliding_window_normalization(
                trace_df[col].to_numpy(),
                True if (normalization_mode == 12) else False,
                normalization_sliding_window,
            )
        elif normalization_mode == 13:
            norm_trace_df[col] = baseline_normalization(
                trace_df[col].to_numpy(),
                normalization_baseline_window
            )
        else:
            norm_trace_df[col] = trace_df[col].to_numpy(),
    return norm_trace_df


def create_peak_df(selected_peaks: list) -> pd.DataFrame:
    peak_df = pd.DataFrame(
        selected_peaks,
        columns=[
            "Filename",
            "ROI#",
            "Frame",
            "abs. Amplitude",
            "rel. Amplitude",
            "abs. norm. Amplitude",
            "rel. norm. Amplitude",
            "evoked",
            "automatic detected peak",
            "decay constant (tau)",
            "inv. decay constant (invtau)",
        ],
    )
    return peak_df


def create_fraction_first_pulse_df(
    peaks: pd.DataFrame, stimulation_timepoints: list[int], patience_l: int, patience_r: int
) -> pd.DataFrame:
    responses = 0
    total_synapses = 0
    for roi in peaks["ROI#"].unique():
        if (
            peaks[
                (peaks["Frame"] >= stimulation_timepoints[0] - patience_l)
                & (peaks["Frame"] <= stimulation_timepoints[0] + patience_r)
                & (peaks["ROI#"] == roi)
            ].shape[0]
            > 0
        ):
            responses += 1
        total_synapses += 1
    return pd.DataFrame(
        {
            "No. responses first pulse": [responses],
            "total detected synapses": [total_synapses],
            "fraction responding": [responses / total_synapses],
            "stimulation frame": [stimulation_timepoints[0]],
            "left patience for response": [patience_l],
            "right patience for response": [patience_r],
        }
    )


def create_stimulation_df(
    stimulations: list[int], patience_l: int, patience_r: int, responses: pd.DataFrame
) -> pd.DataFrame:
    stimulation_list = []
    filename = responses.loc[0, "Filename"]
    for roi in responses["ROI#"].unique():
        responses_roi = responses[responses["ROI#"] == roi]
        for stimulation in stimulations:
            responses_stim = responses_roi[
                (responses_roi["Frame"] >= stimulation - patience_l)
                & (responses_roi["Frame"] <= stimulation + patience_r)
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


def create_ppr_df(
    peaks: pd.DataFrame, stimulation_timepoints: list[int], patience_l: int, patience_r: int
) -> pd.DataFrame:
    result = []
    for roi in peaks["ROI#"].unique():
        roi_response = []
        response_for_each_pulse = True
        first_pulse_response_abs = np.nan
        first_pulse_response_rel = np.nan
        for i, stimulation in enumerate(stimulation_timepoints):
            if (
                peaks[
                    (peaks["Frame"] >= stimulation - patience_l)
                    & (peaks["Frame"] <= stimulation + patience_r)
                    & (peaks["ROI#"] == roi)
                ].shape[0]
                == 0
            ):
                response_for_each_pulse = False
                roi_response.append(
                    [f"Pulse {i+1}", roi, np.nan, np.nan, np.nan, np.nan]
                )
                continue
            max_response_rel = peaks[
                (peaks["Frame"] >= stimulation - patience_l)
                & (peaks["Frame"] <= stimulation + patience_r)
                & (peaks["ROI#"] == roi)
            ]["rel. Amplitude"].max()
            max_response_abs = peaks[
                (peaks["Frame"] >= stimulation - patience_l)
                & (peaks["Frame"] <= stimulation + patience_r)
                & (peaks["ROI#"] == roi)
            ]["abs. Amplitude"].max()
            if np.isnan(first_pulse_response_abs):
                first_pulse_response_abs = max_response_abs
                first_pulse_response_rel = max_response_rel
            ppr_tmp_abs = max_response_abs / first_pulse_response_abs
            ppr_tmp_rel = max_response_rel / first_pulse_response_rel
            roi_response.append(
                [
                    f"Pulse {i+1}",
                    roi,
                    max_response_rel,
                    max_response_abs,
                    ppr_tmp_abs,
                    ppr_tmp_rel,
                ]
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
            "PPR_abs",
            "PPR_rel",
            "responded to all pulses",
        ],
    )


def create_settings_df(settings_dict: dict) -> pd.DataFrame:
    tmp = []
    for key, val in settings_dict.items():
        tmp.append([key, val])
    return pd.DataFrame(tmp, columns=["Option", "Set Value"])


def write_excel_output(
    dataframes: list[pd.DataFrame], df_names: list[str], export_path: str
) -> None:
    with pd.ExcelWriter(export_path) as writer:
        for df, sheet_name in zip(dataframes, df_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
