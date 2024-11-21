from scipy.optimize import curve_fit
import numpy as np


def compute_tau(voltage: np.ndarray) -> tuple[float, float]:
    """
    Fit an exponential curve to calculate the decay constant tau.
    """
    """def exp_decay(t, V0, tau):
        return V0 * np.exp(-t / tau)"""

    def exp_decay(t, y0, A, invTau):
        return y0 + A * np.exp(-t * invTau)

    if len(voltage) <= 1:
        return (np.nan, np.nan)
    frames = [i for i in range(len(voltage))]
    try:
        params, _ = curve_fit(exp_decay, frames, voltage, maxfev=5000)
    except:
        return (np.nan, np.nan)
    inv_tau = params[2]
    tau = 1 / inv_tau
    return (inv_tau, tau)
