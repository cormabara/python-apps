"""
This module contain the model for the new PLL on the input phases
"""
import math

import numpy as np

from f_dice.lib.my_pid import MyPid


class PhasesPll:

    def __init__(self):
        self.ref_omega = None
        self.sin_output = None
        self.msecRange = None
        self.sin_input = None
        self.factor = None
        self.in_teta: float = 0
        self.uu: float = 0
        self.zz: float = 0
        self.delta_omega: float = 0
        self.omega: float = 0
        self.out_phi: float = 0
        self.last_out_phi: float = 0
        self.error: float = 0
        self.output: float = 0

        self.Ki1 = 0.4
        self.ShiftKi1 = 0
        self.Kp1 = 1.5
        self.ShiftKp1 = 0
        self.Ki2 = 1
        self.ShiftKi2 = 0
        self.Ki3 = 0.1
        self.ShiftKi3 = 0

        self.freqPi = MyPid()
        self.freqPi.setIntegral(self.Ki1, self.ShiftKi1)
        self.freqPi.setProportional(self.Kp1, self.ShiftKp1)

        self.freqInt = MyPid()
        self.freqInt.setIntegral(self.Ki2, self.ShiftKi2)

        self.amplInt = MyPid()
        self.amplInt.setIntegral(self.Ki3, self.ShiftKi3)

    def Iterate(self, in_: float):
        """This function execute a single iteration on the PLL using the previous value of the output
            memorized into the last out phi value"""
        self.in_teta = in_
        # Calculation of the sinusoidal input
        self.uu = math.sin(self.in_teta)
        # Calculation of the error
        self.error = self.uu - math.sin(self.last_out_phi)
        # Calculation of the PI input
        self.zz = self.error * math.cos(self.last_out_phi)
        # output of the PI
        self.delta_omega = self.freqPi.output(self.zz)
        self.omega = self.delta_omega + self.ref_omega
        # Integration to obtain the angle
        self.out_phi = self.freqInt.output(self.omega) % (2 * math.pi)
        self.last_out_phi = self.out_phi
        self.output = math.sin(self.last_out_phi)

    def Stimulus(self, amplitude_, frequency_hz_, msDeep_):
        self.msecRange = np.arange(0 , msDeep_, 1)
        self.ref_omega = 2 * math.pi * frequency_hz_
        angle = self.ref_omega * self.msecRange / 1000
        self.sin_input = np.sin(angle)
        self.sin_output = [float(0) for _ in self.msecRange]
        for index in self.msecRange:
            self.Iterate(angle[index])
            self.sin_output[index] = self.output



