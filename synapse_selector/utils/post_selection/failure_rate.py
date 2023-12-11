import pandas as pd


def failure_rate(peaks: pd.DataFrame,
                 stimulation_timepoints: list[int],
                 patience: int) -> pd.DataFrame:
    result = []
    for roi in peaks["ROI#"].unique():
        responses = 0
        for stimulation in stimulation_timepoints:
            if peaks[(peaks['Frame'] >= stimulation) &
                     (peaks['Frame'] <= stimulation+patience) &
                     (peaks['ROI#'] == roi)].shape[0] > 0:
                responses += 1
        rate = responses / len(stimulation_timepoints)
        result.append([roi, rate])
    return pd.DataFrame(result, columns=['ROI', 'response rate'])
