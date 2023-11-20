from scipy.signal import find_peaks
import numpy as np


def peak_detection_scipy(intenstiy: np.ndarray,
                         threshold: float,
                         stim_used: bool,
                         stim_frames: list[int],
                         patience: int) -> list[int]:
    '''
    Peak detection using scipy.
    '''
    peaks = []
    if stim_used and len(stim_frames) > 0:
        for frame in stim_frames:
            tmp_peaks, _ = find_peaks(intenstiy[frame-1:frame+patience+1], height=threshold)
            peaks += [peak+frame-1 for peak in tmp_peaks]
    else:
        tmp_peaks, _ = find_peaks(intenstiy, height=threshold)
        peaks += list(tmp_peaks)
    # specifically for stimulation used it might happen that peaks are detected
    # twice, when the patience window is higher than the time between two
    # consecutive pulses
    peaks = sorted(list(set(peaks)))
    return peaks
