import numpy as np


def compute_threshold(
    vals: np.ndarray,
    threshold_mult: float,
) -> float:
    """
    Function that computes the threshold below which signal is considered to be noise.
    Formula: threshold = mean + std * mult
    """
    # Simplified threshold detection. I don't know whether there was a reason to restrict the calculations in case of stimulation to only by default 0:50 frames,
    # but at least with the new algorithm there should be no reason to use a seperate definition

    return np.mean(vals) + np.std(vals)*threshold_mult