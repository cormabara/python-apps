import math
from collections import deque

import numpy
import numpy as np
from mb_common_lib.types import S32, S32_MIN, S32_MAX
from numpy import int32

from f_dice.lib.my_adc import ADConv
from f_dice.lib.my_trigo import DirClarke, DirPark, TRIGO_THETA_RANGE, TRIGO_SHIFT
from f_dice.lib.my_pid import MyPid
from f_dice.lib.tools import shift_dx, shift_sx


class Pll_2:
    AMPLITUDE_MAX = 500
    ADC_NUMBITS = 14
    FREQUENCY_REF = 50
    OMEGA_REF_HZ = 2 * math.pi * FREQUENCY_REF
    PLL_BAND = 20
    ADCONV_BITS = 16

    PI_KP_VAL = 0
    PI_KP_SHIFT = 6
    PI_KI_VAL = 0
    PI_KI_SHIFT = 6

    I_KI_SHIFT = 16

    REAL_THETA_MUL = TRIGO_THETA_RANGE
    REAL_THETA_DIV = 2 * math.pi
    REAL_THETA_FACTOR = REAL_THETA_MUL / REAL_THETA_DIV
    GAMMA_FACTOR1 = (PLL_BAND * 2 * math.pi) ** 2
    GAMMA_FACTOR2 = (PLL_BAND * 2 * math.pi) * 2

    NEWSHIFT = 6

    def __init__(self, sample_frequency_, deep_):
        self.Beta = 0
        self.Alpha = 0
        self.frequency_in = 0
        self.amplitude_in = 0
        self.step = 0
        self.sample_frequency_hz = sample_frequency_
        self.deep = deep_

        # Variabili di input
        self.theta_in_rad = 0
        self.omega_in_rad = 0
        self.in_sinU = 0
        self.cosW = None
        self.cosV = None
        self.cosU = None
        self.theta_park = 0

        # Variabili di output
        self.theta_out_rad = None
        self.omega_out = 0
        self.out_sinU = 0

        # Variabile di appoggio
        self.prev_theta_in = 0
        self.prev_theta_out = 0
        self.alpha_beta = None
        self.ed_eq = None
        self.effort = None

        # devices
        self.my_pi = MyPid()
        self.my_integrator = MyPid()
        self.adc = ADConv(0, self.AMPLITUDE_MAX, self.ADC_NUMBITS)

        # Settatura del fattore dell'integrale
        self.i_ki = ((2 ** self.I_KI_SHIFT) / self.sample_frequency_hz)
        self.my_integrator.setIntegral(self.i_ki, self.I_KI_SHIFT)

    def stimulus(self, amplitude_, frequency_):
        self.step = 2 * math.pi * frequency_ / self.sample_frequency_hz
        self.amplitude_in = amplitude_
        self.frequency_in = frequency_
        self.omega_in_rad = (self.frequency_in * 2 * math.pi)
        print(str(self.frequency_in))
        print(str(self.omega_in_rad))


    def _loopCreateInputs(self, theta_rad_):
        """This function prepare all inputs for the PLL calculation"""
        self.theta_in_rad = theta_rad_
        self.theta_in_trigo = (theta_rad_ * self.REAL_THETA_FACTOR) % self.REAL_THETA_MUL
        self.omega_in_rad = (self.frequency_in * 2 * math.pi)
        self.in_sinU = self.amplitude_in * math.sin(theta_rad_)
        cosU = self.amplitude_in * math.cos(theta_rad_)
        cosV = self.amplitude_in * math.cos(theta_rad_ - ((2 * math.pi) / 3))
        cosW = self.amplitude_in * math.cos(theta_rad_ - ((4 * math.pi) / 3))

        self.in_sinU = self.adc.convert(self.in_sinU)
        self.cosU = self.adc.convert(cosU)
        self.cosV = self.adc.convert(cosV)
        self.cosW = self.adc.convert(cosW)

    def _loop_ApplyPark(self, rm_):
        """"""
        if (rm_):
            self.theta_park = self.prev_theta_out % self.REAL_THETA_MUL
            # self.teta_park = self.theta_in_1024
        else:
            self.theta_park = (self.prev_theta_out / self.REAL_THETA_FACTOR) % (2 * math.pi)
            # obj.teta_park = obj.theta_in_rad;
        self.ed_eq = DirPark(rm_, self.Alpha, self.Beta, self.theta_park, S32_MIN, S32_MAX)
        self.Ed = self.ed_eq[0]
        self.Eq = self.ed_eq[1]

        if rm_:
            self.Ed = int32(shift_dx(self.Ed, TRIGO_SHIFT - self.NEWSHIFT))
            self.Eq = int32(shift_dx(self.Eq, TRIGO_SHIFT - self.NEWSHIFT))
        else:
            self.Ed = self.Ed * (2 ** self.NEWSHIFT)
            self.Eq = self.Eq * (2 ** self.NEWSHIFT)

    def _loop_PidParsCalculation(self, rm_):
        if rm_:
            # Qui entriamo con Ed ed Eq che sono shiftati a sinistra di NEWSHIFT
            Ed_ = int32(shift_dx(self.Ed, self.NEWSHIFT))
            Eq_ = int32(shift_dx(self.Eq, self.NEWSHIFT))
            tmp = (Ed_ * Ed_) + (Eq_ * Eq_)
            Eg = int32(math.sqrt(tmp));
            pi_kp = shift_sx(self.GAMMA_FACTOR2, self.PI_KP_SHIFT)
            pi_ki = shift_sx(self.GAMMA_FACTOR1, self.PI_KI_SHIFT)
            self.pi_kp = int32(pi_kp / Eg)
            self.pi_ki = int32(pi_ki / Eg)
        else:
            Eg = math.sqrt((self.Ed ** 2) + (self.Eq ** 2))
            Eg = Eg / (2 ** self.NEWSHIFT)
            pi_kp = self.GAMMA_FACTOR2 * (2 ** self.PI_KP_SHIFT)
            pi_ki = self.GAMMA_FACTOR1 * (2 ** self.PI_KI_SHIFT)
            self.pi_kp = pi_kp / Eg
            self.pi_ki = pi_ki / Eg

        self.my_pi.setIntegral(self.pi_ki, self.PI_KI_SHIFT)
        self.my_pi.setProportional(self.pi_kp, self.PI_KP_SHIFT)

    def _loopCalculateOutputs(self):

        tmp_omega = self.effort + (self.OMEGA_REF_HZ * (2 ** self.NEWSHIFT))

        tmp_teta = self.my_integrator.outputPI(tmp_omega)
        self.theta_out_1024 = ((tmp_teta * self.REAL_THETA_FACTOR) / (2 ** self.NEWSHIFT)) % self.REAL_THETA_MUL
        self.prev_theta_out = self.theta_out_1024

        self.omega_out = tmp_omega / (2 ** self.NEWSHIFT)

        self.real_teta_out = tmp_teta
        self.real_omega_out = tmp_omega
        self.theta_out_rad = (self.theta_out_1024 / self.REAL_THETA_FACTOR) % (2 * math.pi)
        self.out_sinU = (self.Ed / (2**self.NEWSHIFT)) * math.sin(self.theta_out_rad)

    def Calculate(self, real_, theta_in_):
        """This function execute a single iteration on the PLL using the previous value of the output
            memorized into the last out phi value"""

        self._loopCreateInputs(theta_in_)

        self.alpha_beta = DirClarke(real_, self.cosU, self.cosV, self.cosW, S32_MIN, S32_MAX)
        self.Alpha = self.alpha_beta[0]
        self.Beta = self.alpha_beta[1]

        self._loop_ApplyPark(real_)

        self._loop_PidParsCalculation(real_)

        self.effort = self.my_pi.outputPI(self.Eq)

        self._loopCalculateOutputs()

