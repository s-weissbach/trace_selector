import numpy as np
import numpy.typing as npt


def sliding_window_normalization(
        trace: np.ndarray, 
        use_median: bool = True, 
        window_size: int = 50,
) -> npt.NDArray[np.float64]:
    """
    Normalize a 1D numpy array using a sliding window.

    :param (np.ndarray) trace: Input 1D array to be normalized.
    :param (bool) use_median: If True, use median for normalization; else, use mean.
    :param (int) window_size: Size of the sliding window.
    :return (np.ndarray): Normalized array.
    """
    if not isinstance(trace, np.ndarray) or trace.ndim != 1:
        raise ValueError("Input 'trace' must be a 1D numpy array.")

    if len(trace) == 0:
        raise ValueError("Input array 'trace' is empty.")

    if window_size >= len(trace):
        raise ValueError(
            "Window size should be smaller than the length of the input array."
        )

    window_before = window_size // 2
    window_after = window_size // 2
    norm_trace = np.empty_like(trace, dtype=np.float64)

    for pos, dp in enumerate(trace):
        norm_window_start = max(0, pos - window_before)
        norm_window_end = min(pos + window_after, len(trace) - 1)

        # Calculate normalization factor
        norm_factor = (
            np.median(trace[norm_window_start:norm_window_end])
            if use_median
            else np.mean(trace[norm_window_start:norm_window_end])
        )

        # Normalize data point and assign to result array
        norm_trace[pos] = dp / norm_factor

    return norm_trace


def baseline_normalization(
        trace: np.ndarray, 
        frame_subset: tuple[int,int]
        ) -> npt.NDArray[np.float64]:
    """
    Normalize the trace using a subset of it

    :param (np.ndarray) trace: Input 1D array to be normalized.
    :param (tuple[int,int]) frame_subset: The interval for the baseline normalization
    :return (np.ndarray): Normalized array.
    """
    t = trace[frame_subset[0]:frame_subset[1]]
    if len(t) == 0: # TODO: Maybe implement here a error handling
        median = 1
    else:
        median = np.median(t) 

    return t / median