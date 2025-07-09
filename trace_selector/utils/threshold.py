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
    # 2025-07-09 Added back a modern version of the threshold subset code. But it will not be used (yet) as I still do not see the point of this setting.
    # 2024-?: Simplified threshold detection. I don't know whether there was a reason to restrict the calculations in case of stimulation to only by default 0:50 frames,
    # but at least with the new algorithm there should be no reason to use a seperate definition

    if frame_subset is not None:
        vals = vals[frame_subset[0]:frame_subset[1]]

    return float(np.mean(vals) + np.std(vals)*threshold_mult)