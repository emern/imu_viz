"""
Low pass filter designed to be analog of RC lowpass
"""

import math
import numpy as np

class RCFilter:

    """
    based on TF of RC lowpass filter:
    (1-vo)/r = (vo/(1/cs))
    TF = 1/(1+r*c*s)
    Pole of TF at 1/(r*c)

    Must choose some constants R and C such that they give the desired lowpass

    We will discretize this using backwards euler method (dV/dt = (v[n] - v[n-1])/T)
    ODE for this equation becomes Vin = Vout + RCdVout/dt

    Cutoff frequency at 1/(2*pi*r*c) hz
    """
    def __init__(self, cutoff : int, sample_time : float) -> None:
        self.c = 0.1
        self.r = 1/(cutoff * self.c * 2 * math.pi)
        self.sample_time = sample_time

        # Check Nyquist limits
        if (cutoff*2 > (1/sample_time)):
            raise Exception("check RC filter cutoff values!")

        self.last = None
        self.running = False

    """
    Filter method, to be used on whole input vectors for efficiency
    """
    def filter(self, current : np.ndarray):

        if self.running == False:
            self.last = np.zeros(current.shape)
            self.running = True

        new_vals = current * (self.sample_time / (self.sample_time + self.r*self.c)) + ((self.r*self.c/(self.sample_time + self.r*self.c)) * self.last)
        self.last = new_vals
        return new_vals

if __name__ == '__main__':
    pass
