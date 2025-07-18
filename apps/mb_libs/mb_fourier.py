import numpy as np
from scipy.fft import fft, fftfreq

def to_fourier(in_):
    samples = len(in_)
    spacing = 1 / 10000
    # Compute the FFT
    yf = fft(in_)
    xf = fftfreq(samples, spacing)[:samples // 2]
    yff = 2.0 / samples * np.abs(yf[0:samples // 2])
    return xf,yf,yff
