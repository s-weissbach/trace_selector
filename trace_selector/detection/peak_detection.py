from scipy.signal import find_peaks
import numpy as np


def peak_detection_scipy(
    intensity: np.ndarray,
    threshold: float,
    prominence: float,
    minDistance: int,
    stim_used: bool,
    stim_frames: list[int],
    patience_l: int,
    patience_r: int,
) -> list[int]:
    """
    Peak detection using scipy.
    """

    if stim_used and len(stim_frames) > 0:
        peaks = []
        for frame in stim_frames:
            tmp_peaks, _ = find_peaks(intensity[frame - 1 - patience_l: frame + 1 + patience_r], height=threshold, distance=minDistance, prominence=prominence)
            peaks += [peak + frame - 1 for peak in tmp_peaks]
        # specifically for stimulation used it might happen that peaks are detected
        # twice, when the patience window is higher than the time between two
        # consecutive pulses     
        return sorted(list(set(peaks)))
    return list(find_peaks(intensity, height=threshold, distance=minDistance, prominence=prominence)[0])
