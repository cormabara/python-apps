


import math
from collections import deque

import numpy as np

from report import rpt_print
from my_types import S32_MIN, S32_MAX, U32
from numpy import int32

from my_adc import ADConv
from my_trigo import trigo_dir_clarke, trigo_dir_park, TRIGO_THETA_RANGE, TRIGO_SHIFT
from my_pid import MyPid
from tools import shift_dx, shift_sx, CheckUnsigned32, CnfAfe


class PhasesPll:
    AMPLITUDE_MAX = 500
    ADC_NUMBITS = 12
    FREQUENCY_REF_HZ = 50
    OMEGA_REF_RAD = 2 * math.pi * FREQUENCY_REF_HZ
    PLL_BAND = 1000

    THETA_CUSTOM_RANGE = TRIGO_THETA_RANGE
    THETA_RAD_RANGE = 2 * math.pi
    THETA_RAD_TO_CUSTOM = THETA_CUSTOM_RANGE / THETA_RAD_RANGE
    THETA_CUSTOM_TO_RAD = THETA_RAD_RANGE / THETA_CUSTOM_RANGE
    GAMMA_FACTOR1 = (PLL_BAND * 2 * math.pi) ** 2
    GAMMA_FACTOR2 = (PLL_BAND * 2 * math.pi) * 2

    PI_KP_VAL = 0.1
    PI_KP_SHIFT = 8
    PI_KI_VAL = 0.4
    PI_KI_SHIFT = 8
    I_KI_SHIFT = 16
    NEW_SHIFT = 0

    def __init__(self, rm_, sample_frequency_hz_, deep_):

        self.in_t = None
        self.in_s = None
        self.in_r = None
        self.sample_frequency_hz = sample_frequency_hz_
        self.deep = deep_
        self.real_mode = rm_
        # Variabili di input
        self.theta_in_custom = 0
        self.theta_in_rad = 0
        self.omega_in_rad = 0
        self.in_sinU = 0
        self.cosW = None
        self.cosV = None
        self.cosU = None
        self.theta_park = 0

        # Variabili di output
        self.theta_out_custom = None
        self.theta_out_rad = None
        self.omega_out_rad = 0
        self.out_sinU = 0

        # Variabile di appoggio
        self.Beta = 0
        self.Alpha = 0
        self.Ed = 0
        self.Eq = 0
        self.Eg = 0
        self.frequency_in = 0
        self.amplitude_in = 0

        self.prev_theta_out_custom = 0         # Feedback of theta in custom unit
        self.alpha_beta = None
        self.ed_eq = None
        self.effort = None

        # devices
        self.my_pi = MyPid(rm_)
        self.my_integrator = MyPid(rm_)
        self.adc = ADConv(0, self.AMPLITUDE_MAX, self.ADC_NUMBITS)

        # Settatura del fattore dell'integrale
        self.i_ki = ((2 ** self.I_KI_SHIFT) / self.sample_frequency_hz)
        self.my_integrator.setIntegral(self.i_ki, self.I_KI_SHIFT)

        self.BASE_STEP_CUSTOM = TRIGO_THETA_RANGE * self.FREQUENCY_REF_HZ / self.sample_frequency_hz

        wr = CnfAfe().WIN_DEEP
        self.display_range = CnfAfe().display_range()

        iniVal = [float(0) for i in self.display_range]


        # set delle grandezze vettoriali in loop
        self.vector_index = deque([i for i in self.display_range], maxlen=wr)
        self.input_sequence_v = deque(iniVal, maxlen=wr)
        self.theta_in_custom_v = deque(iniVal, maxlen=wr)
        self.theta_in_rad_v = deque(iniVal, maxlen=wr)
        self.omega_in_v = deque(iniVal, maxlen=wr)
        self.in_sinU_v = deque(iniVal, maxlen=wr)

        self.in_r_v = deque(iniVal, maxlen=wr)
        self.in_s_v = deque(iniVal, maxlen=wr)
        self.in_t_v = deque(iniVal, maxlen=wr)


        self.inputCosW_v = deque(iniVal, maxlen=wr)
        self.inputCosV_v = deque(iniVal, maxlen=wr)
        self.inputCosU_v = deque(iniVal, maxlen=wr)

        self.alpha_v = deque(iniVal, maxlen=wr)
        self.beta_v = deque(iniVal, maxlen=wr)

        self.eq_v = deque(iniVal, maxlen=wr)
        self.ed_v = deque(iniVal, maxlen=wr)
        self.eg_v = deque(iniVal, maxlen=wr)
        self.effort_v = deque(iniVal, maxlen=wr)
        self.prev_theta_out_v = deque(iniVal, maxlen=wr)
        self.pi_kp_v = deque(iniVal, maxlen=wr)
        self.pi_ki_v = deque(iniVal, maxlen=wr)
        self.theta_park_v = deque(iniVal, maxlen=wr)

        self.omega_out_v = deque(iniVal, maxlen=wr)
        self.theta_out_rad_v = deque(iniVal, maxlen=wr)
        self.theta_out_custom_v = deque(iniVal, maxlen=wr)
        self.out_sinU_v = deque(iniVal, maxlen=wr)

    def _createStimulus(self, amplitude_, frequency_):
        self.amplitude_in = amplitude_
        self.frequency_in = frequency_
        self.omega_in_rad = (self.frequency_in * 2 * math.pi)
        print(str(self.frequency_in))
        print(str(self.omega_in_rad))

    def _create_inputs(self, theta_custom_):
        """This function prepare all inputs for the PLL calculation"""
        self.theta_in_custom = theta_custom_ % self.THETA_CUSTOM_RANGE
        self.theta_in_rad = (self.theta_in_custom * self.THETA_CUSTOM_TO_RAD) % self.THETA_RAD_RANGE
        self.omega_in_rad = (self.frequency_in * 2 * math.pi)
        self.in_sinU = self.amplitude_in * math.sin(self.theta_in_rad)
        cosU = self.amplitude_in * math.cos(self.theta_in_rad)
        cosV = self.amplitude_in * math.cos(self.theta_in_rad - ((2 * math.pi) / 3))
        cosW = self.amplitude_in * math.cos(self.theta_in_rad - ((4 * math.pi) / 3))

        self.in_sinU = self.adc.convert(self.in_sinU)
        # self.cosU = self.adc.convert(cosU)
        # self.cosV = self.adc.convert(cosV)
        # self.cosW = self.adc.convert(cosW)
        self.cosU = cosU
        self.cosV = cosV
        self.cosW = cosW

    def _apply_park(self):
        """ Routine di applicazione della park. IN real mode l'angolo è in unità custom, in theo mode
            è invece espresso in radianti """
        if self.real_mode:
            self.theta_park = self.prev_theta_out_custom % self.THETA_CUSTOM_RANGE
            # self.theta_park = self.theta_in_custom
        else:
            self.theta_park = (self.prev_theta_out_custom * self.THETA_CUSTOM_TO_RAD) % (2 * math.pi)
            # self.theta_park = self.theta_in_rad

        self.ed_eq = trigo_dir_park(self.real_mode, self.Alpha, self.Beta, self.theta_park, S32_MIN, S32_MAX)
        self.Ed = self.ed_eq[0]
        self.Eq = self.ed_eq[1]

        if self.real_mode:
            self.Ed = int32(shift_dx(self.Ed, TRIGO_SHIFT - self.NEW_SHIFT))
            self.Eq = int32(shift_dx(self.Eq, TRIGO_SHIFT - self.NEW_SHIFT))
        else:
            self.Ed = self.Ed * (2 ** self.NEW_SHIFT)
            self.Eq = self.Eq * (2 ** self.NEW_SHIFT)

    def _pid_pars_calculation(self):
        if self.real_mode:
            # Qui entriamo con Ed ed Eq che sono shiftati a sinistra di NEWSHIFT
            Ed_ = float(shift_dx(self.Ed, self.NEW_SHIFT))
            Eq_ = float(shift_dx(self.Eq, self.NEW_SHIFT))
            Ed_2 = Ed_ * Ed_
            if CheckUnsigned32(Ed_2):
                rpt_print("Overflow on Eg calculation 1")
            Eq_2 = Eq_ * Eq_
            if CheckUnsigned32(Eq_2):
                rpt_print("Overflow on Eg calculation 2")
            eg_tmp = (Ed_ * Ed_) + (Eq_ * Eq_)
            if CheckUnsigned32(eg_tmp):
                rpt_print("Overflow on Eg calculation 3")
            self.Eg = int32(math.sqrt(eg_tmp))
            pi_kp = shift_sx(int(self.GAMMA_FACTOR2), self.PI_KP_SHIFT)
            if CheckUnsigned32(pi_kp):
                rpt_print("Overflow on Eg calculation 4")
            pi_ki = shift_sx(int(self.GAMMA_FACTOR1), self.PI_KI_SHIFT)
            if CheckUnsigned32(pi_ki):
                rpt_print("Overflow on Eg calculation 5")
            self.pi_kp = int32(pi_kp / self.Eg)
            self.pi_ki = int32(pi_ki / self.Eg)
        else:
            self.Eg = math.sqrt((self.Ed ** 2) + (self.Eq ** 2))
            self.Eg = self.Eg / (2 ** self.NEW_SHIFT)
            pi_kp = self.GAMMA_FACTOR2 * (2 ** self.PI_KP_SHIFT)
            pi_ki = self.GAMMA_FACTOR1 * (2 ** self.PI_KI_SHIFT)
            self.pi_kp = pi_kp / self.Eg
            self.pi_ki = pi_ki / self.Eg

        self.my_pi.setIntegral(self.pi_ki, self.PI_KI_SHIFT)
        self.my_pi.setProportional(self.pi_kp, self.PI_KP_SHIFT)

    def _calculate_outputs(self):

        ref_omega = self.OMEGA_REF_RAD * (2 ** self.NEW_SHIFT)
        tmp_omega_rad_shifted = self.effort  + ref_omega
        tmp_theta_rad_shifted = self.my_integrator.output(tmp_omega_rad_shifted)
        self.omega_out_rad = tmp_omega_rad_shifted / (2 ** self.NEW_SHIFT)

        self.theta_out_custom = (tmp_theta_rad_shifted * self.THETA_RAD_TO_CUSTOM) / (2 ** self.NEW_SHIFT)
        self.theta_out_custom %= self.THETA_CUSTOM_RANGE
        self.prev_theta_out_custom = self.theta_out_custom


        self.theta_out_rad = (self.theta_out_custom * self.THETA_CUSTOM_TO_RAD) % (2 * math.pi)
        self.out_sinU = (self.Ed / (2 ** self.NEW_SHIFT)) * math.sin(self.theta_out_rad)

    def get_theta_custom(self):
        return self.theta_out_custom

    def get_omega(self):
        return self.omega_out_rad

    def calculate(self, in_r_, in_s_, in_t_):
        """This function execute a single iteration on the PLL using the previous value of the output
            memorized into the last out phi value"""
        self.in_r = in_r_
        self.in_s = in_s_
        self.in_t = in_t_

        self.alpha_beta = trigo_dir_clarke(self.real_mode, self.in_r, self.in_s, self.in_t, S32_MIN, S32_MAX)
        self.Alpha = self.alpha_beta[0]
        self.Beta = self.alpha_beta[1]

        self._apply_park()

        # self._loop_PidParsCalculation()

        self.effort = self.my_pi.output(self.Eq)

        self._calculate_outputs()
        self.plot_sample()

    def calculate_loop(self, amplitude_, frequency_):
        self._createStimulus(amplitude_, frequency_)

        self.prev_theta_out_custom = 0
        theta_in = 0
        # Il for viene definito sul numero di campioni calcolati per il
        # teta di ingresso
        for sample in self.display_range:
            self.calculate(theta_in)
            self.plot_sample(sample)
            theta_in += self.BASE_STEP_CUSTOM
            self.input_sequence_v.append(theta_in)
        # Torno nel calcolo teorico per salvare vars per il confronto con il caso teorico
        self.out_amplitude = float(np.mean(self.ed_v) / 2 ** self.NEW_SHIFT)

    def plot_sample(self):
        self.in_sinU_v.append(self.in_sinU)
        self.inputCosU_v.append(self.cosU)
        self.inputCosV_v.append(self.cosV)
        self.inputCosW_v.append(self.cosW)
        self.theta_in_custom_v.append(self.theta_in_custom)
        self.theta_in_rad_v.append(self.theta_in_rad)
        self.omega_in_v.append(self.omega_in_rad)

        self.in_r_v.append(self.in_r)
        self.in_s_v.append(self.in_s)
        self.in_t_v.append(self.in_t)

        self.alpha_v.append(self.Alpha)
        self.beta_v.append(self.Beta)
        self.theta_park_v.append(self.theta_park)
        self.ed_v.append(self.Ed)
        self.eq_v.append(self.Eq)
        self.eg_v.append(self.Eg)
        # self.pi_ki_v.append(self.pi_ki)
        # self.pi_kp_v.append(self.pi_kp)
        self.effort_v.append(self.effort)
        self.prev_theta_out_v.append(self.prev_theta_out_custom)
        self.theta_out_custom_v.append(self.theta_out_custom)
        self.theta_out_rad_v.append(self.theta_out_rad)
        self.omega_out_v.append(self.omega_out_rad)
        self.out_sinU_v.append(self.out_sinU)
