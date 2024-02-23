""" This is a PLL per the lock of a encoder
Starting from the real position in angle (0-1023) we calculate the speed error through a PID and then
with integrator we calculate the obs_pos position. This ob_pos is used to calculate the error from real_pos
"""

from my_pid import MyPid
from my_pid import XIntegral
from range_limits import wrap_out_of_range
from report import rpt_print
from tools import CheckSigned32
from my_types import S32_MAX, S16_MAX, U32_MAX, S32


class PllEncoder:
    """Simple PLL that locks the position and speed of a generic a/b encoder
        Input and out put variables are:
        - For pos in encoder tick
        - For the speed in tick/sample where sample is the sample time of the PLL """

    def __init__(self, realmode_, encoder_resolution_, sample_freq_hz_, with_ff_):
        """Constructor: Create the PLL ENCODER
            Parameters:
            - Encoder resolution
            - Activate the feed forward """
        self.__realMode = realmode_
        self.deltaPos = None  # Delta di posizione su 1ms
        self.enc_res = encoder_resolution_
        self.sample_freq_hz = sample_freq_hz_

        # encoder 1024 - 16383
        # frequency 5000 - 2500
        # factor = encoder / (256*sample_freq) = (encoder/sample_freq)>>8
        # Quindi scelgo di avere un fattore shift dx di 16

        num = self.enc_res << 16
        if CheckSigned32(num):
            rpt_print("Error overflow on numerator")

        den = self.sample_freq_hz * 256
        self.rps256_2_ts_factor = S32(num) / S32(den)
        self.with_ff = with_ff_

        self.realPos = None  # posizione reale
        self.realSpeed = 0  # Speed in ingresso
        self.errPos1 = None  # Errore di posizione
        self.errPos2 = None  # Errore di posizione
        self.obsPos: float = 0  # Posizione stimata
        self.effort = None  # Effort del PID

        self.obsSpeed = None  # velocità stimata

        self.pid1 = MyPid(self.__realMode)  # PID from the position error to observed speed
        self.pid1.setProportional(1, 0)
        self.pid1.setIntegral(1, 0)

        self.obsSpeedIntegral = XIntegral(self.__realMode)

    def setProportional(self, kp_, shift_kp_):
        self.pid1.setProportional(kp_, shift_kp_)

    def setIntegral(self, ki_, shift_ki_):
        self.pid1.setIntegral(ki_, shift_ki_)

    def setDerivative(self, kd_, shift_kd_):
        self.pid1.setDerivative(kd_, shift_kd_)

    def setLimits(self, antiwindup_min_, antiwindup_max_, integral_limit_):
        self.pid1.setLimits(antiwindup_min_, antiwindup_max_, integral_limit_)

    def calculate(self, pos_, speed_rps256_):
        self.realPos = pos_
        self.realSpeed = speed_rps256_ * self.rps256_2_ts_factor
        self.errPos1 = self.realPos - self.obsPos
        self.errPos2 = wrap_out_of_range(self.errPos1, -self.enc_res / 2, self.enc_res / 2,
                                         self.enc_res)

        self.effort = self.pid1.output(self.errPos2)
        self.obsSpeed = self.effort  # +  (self.realSpeed if self.with_ff else 0)

        self.obsPos = self.obsSpeedIntegral.incrementW(self.effort, 0, 0, self.enc_res - 1, self.enc_res - 1)
