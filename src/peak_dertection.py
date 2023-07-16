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
            tmp_peaks,_ = find_peaks(intenstiy[frame:frame+patience],height=threshold)
            peaks += [peak+frame for peak in tmp_peaks]
    else:
        tmp_peaks,_ = find_peaks(intenstiy,height=threshold)
        peaks += list(tmp_peaks)
    return peaks