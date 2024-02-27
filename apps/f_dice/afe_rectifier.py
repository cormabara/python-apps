"""
In this module the definition of the DICE RECTIFIER application
"""
import math
from dataclasses import dataclass

import numpy as np
from matplotlib import pyplot as plt

from my_sigmadelta import SigmaDelta
from report import MyReport
from vmains import VMains
from my_pid import MyPid

from tools import SinForm, MyPlot, CnfAfe


class InputStage:
    FREQUENCY_HZ = 50
    SAMPLE_TIME_US = 100


class AfeRectifier:

    def __init__(self):
        self.vmains = VMains()

    def start(self):
        self.vmains.start()
        pass

    def execute(self, ph_r_, ph_s_, ph_t_):
        self.vmains.execute(ph_r_, ph_s_, ph_t_)
        pass

    def plot_sample(self):

        pass

