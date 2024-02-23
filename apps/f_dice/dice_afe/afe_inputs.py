""" Inside this file the input situmuls for the dice afe system """

import numpy
import math

import numpy as np


class AfeInputs:
    BASE_FREQUENCY_HZ = 50
    def __init__(self,voltage_,samples_):
        self.amplitude_v = voltage_
        self.samples = samples_
        in_s = numpy.arange(0, (4 * math.pi), (4 * math.pi) / 100)
        self.phR = self.amplitude_v * np.sin(in_s)

        self.phSpos = self.amplitude_v * np.sin(in_s - ((2 * math.pi) / 3))
        self.phTpos = self.amplitude_v * np.sin(in_s - ((4 * math.pi) / 3))

        self.phSneg = self.amplitude_v * np.sin(in_s + ((2 * math.pi) / 3))
        self.phTneg = self.amplitude_v * np.sin(in_s + ((4 * math.pi) / 3))

        self.phRSpos = phR - phSpos
        self.phSTpos = phSpos - phTpos

        self.phRSneg = phR - phSneg
        self.phSTneg = phSneg - phTneg

