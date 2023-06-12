# Class for a IIR filter definition with the same algorithm used inside DICE

import math

class MyIIRFilter:
        _Fsample_Hz : float               # Cut frequency of the filter in Hz
        _Fcut_Hz : float               # Sample frequency in Hz
        _accumulator: float          # Accumulator for the filter

        _Wt: float                   # Time constant of the filter

        def __init__(self,freq_sample_Hz_: float,freq_cut_Hz_: float):
            ''' Constructor of the filter with sample frequency and cut frequeny
            If cut frequency is 0 the filter is disabled '''
            self._Fsample_Hz = freq_sample_Hz_
            self._Fcut_Hz = freq_cut_Hz_
            self._Wt= (self._Fcut_Hz * 2 * math.pi * (pow(2, 16))) / self._Fsample_Hz
            self._accumulator = 0

        # Reset the accumulator of the filter
        def Reset(self):
            self._accumulator = 0

        # Add a sample to filter and return the filtered value
        def Sample(self,sample_):
            if self._Fcut_Hz != 0:
                err = sample_ - self._accumulator/pow(2,16)
                self._accumulator = self._accumulator + (err * self._Wt)
                return self._accumulator/pow(2,16)
            else:
                return sample_

        # Get the value of the filter
        def GetVal(self):
            val = self._accumulator/pow(2,16)



