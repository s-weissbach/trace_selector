import numpy as np


def compute_threshold(
    vals: np.ndarray,
    threshold_mult: float,
    frame_subset: tuple[int,int]|None = None,
) -> float:
    """
    Function that computes the threshold below which signal is considered to be noise.
    Formula: threshold = mean + std * mult

    :param (np.ndarray) vals: the signal array
    :param (float) threshold_mult: Mutliplicator for threshold calculation
    :param (ruple[int,int]|None, optional) frame_subset: If not None, only the slice given by this array is used for threshold detection.
    :return (float): The calculated threshold
    """

    if frame_subset is not None:
        vals = vals[frame_subset[0]:frame_subset[1]]

    return float(np.mean(vals) + np.std(vals)*threshold_mult)