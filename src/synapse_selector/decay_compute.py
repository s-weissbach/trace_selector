from scipy.optimize import curve_fit
import numpy as np

def compute_tau(voltage: list[float]):
    '''
    Fit an exponential curve to calculate the decay constant tau.
    '''
    def exp_decay(t, V0, tau):
        return V0 * np.exp(-t / tau)
    frames = [i for i in range(len(voltage))]
    (_,tau),_ = curve_fit(exp_decay,frames,voltage)
    return tau