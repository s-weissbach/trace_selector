import numpy as np


def compute_threshold(stim_used: bool,
                      vals: np.ndarray,
                      threshold_mult: float,
                      threshold_start: int = 0,
                      threshold_stop: int = 50) -> float:
    '''
    Function that computes the threshold above which a peak is considered spike
    based on the formular threshold = mean + std * mult
    '''
    if stim_used > 0:
        std_ = np.std(vals[threshold_start:threshold_stop])
        mean_ = np.mean(vals[threshold_start:threshold_stop])
        return mean_ + threshold_mult * std_
    std_ = np.std(vals)
    median_ = np.median(vals)
    return median_ + threshold_mult * std_
