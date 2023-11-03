import pandas as pd


def compute_fraction_first_pulse(peaks: pd.DataFrame,
                                 stimulation_timepoints: list[int],
                                 patience: int) -> pd.DataFrame:
    responses = 0
    total_synapses = 0
    for roi in peaks["ROI#"].unique():
        if peaks[(peaks['Frame'] >= stimulation_timepoints[0]) &
                    (peaks['Frame'] <= stimulation_timepoints[0]+patience) &
                    (peaks['ROI#'] == roi)].shape[0] > 0:
            responses += 1
        total_synapses += 1
    return pd.DataFrame({'No. responses first pulse': [responses],
                         'total detected synapses': [total_synapses],
                         'fraction responding': [responses/total_synapses],
                         'stimulation frame': [stimulation_timepoints[0]],
                         'patience for response': [patience]})
