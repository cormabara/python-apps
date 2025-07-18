"""
Inside this file the definition of the PID (proportional-integral-derivative loop and the XIntegral class
to implement a genral integrator (used inside the PID)
"""
import math

from numpy import int32

from config import is_dice
from mb_logger import Logger
from mb_types import S32_MAX, S32_MIN, check_s32, set_s32

# supporto per componente integrale dei PID
from mb_ranges import saturate_out_of_range, wrap_out_of_range


class XIntegral:
    """ This is the basic integral class commutated from DICE. This calss has a mode_ parameter
        used for the DICE behaviour (only integer variables, no divsion exc..."""
    def __init__(self):
        self.val = 0
        self.fractional = 0

    def preset(self, val_):
        self.val = val_
        self.fractional = 0

    def get_val(self):
        return self.val

    def _calculate(self,step_,shift_):
        if is_dice():
            increment = set_s32(step_ / 2 ** shift_)
        else:
            increment = step_ / 2 ** shift_

        return increment

    def increment(self, step_, shift_, limit_):
        """Traditional increment with the simmetric out of range"""
        increment = self._calculate(step_,shift_)
        # calcolo del valore
        self.val = saturate_out_of_range((self.val + increment), -limit_, +limit_)
        return self.val

    def incrementMinMax(self, step_, shift_, min_, max_):
        """ @brief Execute the integral with a saturation reference
            @details If the value of the integral reaches the limits then was saturated to
            the corresponding limit """
        increment = self._calculate(step_,shift_)
        # calcolo del valore
        self.val = saturate_out_of_range((self.val + increment), min_, max_)
        return self.val

    def incrementW(self, step_, shift_, min_, max_, delta_):
        """ @brief execute the integral with a wrap reference
          * @details If the value of the integral reaches the limits then wrap by delta_ """
        increment = self._calculate(step_,shift_)
        # calcolo del valore
        self.val = wrap_out_of_range((self.val + increment), min_, max_, delta_)
        return self.val if (not is_dice()) else set_s32(self.val)

    def reduce(self, shift_):
        self.val -= self.val / 2 ** shift_


class MyPid:
    """This is the basic class for a generic PID module """
    def __init__(self):
        self.prevError = 0
        self.kp = 0
        self.kd = 0
        self.ki = 0
        self.kp_shift = 0  # shift componente proporzionale (per avere pesi frazionari)
        self.shift_kd = 0  # shift componente derivativa (per avere pesi frazionari)
        self.ki_shift = 0  # shift componente integrale (per avere pesi frazionari)
        self.antiwindup_max = S32_MAX
        self.antiwindup_min = S32_MIN
        self.integral_limit = S32_MAX
        self.integral = XIntegral()
        self.reset()

    def setProportional(self, kp_, shift_kp_):
        self.kp = kp_
        self.kp_shift = shift_kp_


    def setIntegral(self, ki_, shift_ki_):
        self.ki = ki_
        self.ki_shift = shift_ki_

    def setDerivative(self, kd_, shift_kd_):
        self.kd = kd_
        self.shift_kd = shift_kd_

    def setLimits(self, antiwindup_min_, antiwindup_max_, integral_limit_):
        self.antiwindup_max = antiwindup_max_
        self.antiwindup_min = antiwindup_min_
        self.integral_limit = integral_limit_
        if is_dice():
            self.antiwindup_max = int32(math.floor(self.antiwindup_max))
            self.antiwindup_min = int32(math.floor(self.antiwindup_min))
            self.integral_limit = int32(math.floor(self.integral_limit))

    def reset(self):
        self.prevError = 0
        self.integral.preset(0)

    def output(self, error_):  # error_ = reference - real
        # componente proporzionale
        out = 0
        if self.kp:
            out = (error_ * self.kp) / 2 ** self.kp_shift
            if not check_s32(out):
                Logger().print("Overflow on mypid proportional")

        # componente derivativa
        if self.kd:
            out += ((error_ - self.prevError) * self.kd) / 2 ** self.shift_kd
            if not check_s32(out):
                Logger().print("Overflow on mypid derivative")

        # componente integrale del campionamento precedente
        if self.ki:
            out += self.integral.get_val()
            if not check_s32(out):
                Logger().print("Overflow on mypid integral")

        self.prev_error = error_

        if not check_s32(out):
            Logger().print("Overflow on mypid output")

        # limitazione anti - windup con aggiornamento dell'errore integrale
        if out <= self.antiwindup_min:
            out = self.antiwindup_min
        elif out >= self.antiwindup_max:
            out = self.antiwindup_max
        else:
            self.integral.increment(error_ * self.ki, self.ki_shift, self.integral_limit)

        if is_dice():
            return set_s32(out)
        else:
            return out
