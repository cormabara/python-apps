"""
Inside this file the definition of the PID (proportional-integral-derivative loop and the XIntegral class
to implement a genral integrator (used inside the PID)
"""
import math

from numpy import int32

from report import rpt_print
from tools import CheckSigned32
from my_types import S32_MAX, S32_MIN


# supporto per componente integrale dei PID
from range_limits import saturate_out_of_range, wrap_out_of_range


class XIntegral:

    def __init__(self,realmode_):
        self.__realMode = realmode_
        self.__myVal = 0
        self.__fractional = 0

    def preset(self, val_: int):
        self.__myVal = val_
        self.__fractional = 0

    def getVal(self):
        return self.__myVal

    def increment(self, step_: float, shift_: int, limit_: float):
        """Traditional increment with the simmetric out of range"""
        increment = step_ / 2 ** shift_
        # calcolo del valore
        self.__myVal = saturate_out_of_range((self.__myVal + increment), -limit_, +limit_)
        return self.__myVal

    def incrementMinMax(self, step_, shift_, min_, max_):
        """ @brief Execute the integral with a saturation reference
            @details If the value of the integral reaches the limits then was saturated to
            the corresponding limit """
        increment = step_ / 2 ** shift_
        # calcolo del valore
        self.__myVal = saturate_out_of_range((self.__myVal + increment), min_, max_)
        return self.__myVal

    def incrementW(self, step_, shift_, min_, max_, delta_):
        """ @brief execute the integral with a wrap reference
          * @details If the value of the integral reaches the limits then wrap by delta_ """
        increment = step_ / 2 ** shift_
        # calcolo del valore
        self.__myVal = wrap_out_of_range((self.__myVal + increment), min_, max_, delta_)
        return self.__myVal

    def reduce(self, shift_):
        self.__myVal -= self.__myVal / 2 ** shift_


class MyPid:

    def __init__(self, realmode_):
        self.__realMode = realmode_
        self.prevError = 0
        self.kp = 0
        self.kd = 0
        self.ki = 0
        self.shift_kp = 0  # shift componente proporzionale (per avere pesi frazionari)
        self.shift_kd = 0  # shift componente derivativa (per avere pesi frazionari)
        self.shift_ki = 0  # shift componente integrale (per avere pesi frazionari)
        self.antiwindup_max = S32_MAX
        self.antiwindup_min = S32_MIN
        self.integral_limit = S32_MAX
        self.integral = XIntegral(self.__realMode)
        self.reset()

    def setProportional(self, kp_, shift_kp_):
        self.kp = kp_
        self.shift_kp = shift_kp_

    def setIntegral(self, ki_, shift_ki_):
        self.ki = ki_
        self.shift_ki = shift_ki_

    def setDerivative(self, kd_, shift_kd_):
        self.kd = kd_
        self.shift_kd = shift_kd_

    def setLimits(self, antiwindup_min_, antiwindup_max_, integral_limit_):
        self.antiwindup_max = antiwindup_max_
        self.antiwindup_min = antiwindup_min_
        self.integral_limit = integral_limit_
        if self.__realMode:
            self.antiwindup_max = int32(math.floor(self.antiwindup_max))
            self.antiwindup_min = int32(math.floor(self.antiwindup_min))
            self.integral_limit = int32(math.floor(self.integral_limit))

    def reset(self):
        self.prevError = 0
        self.integral.preset(0)

    def output(self, error_: float):  # error_ = reference - real
        # componente proporzionale
        out = 0
        if self.kp:
            out = (error_ * self.kp) / 2 ** self.shift_kp
            if not CheckSigned32(out):
                rpt_print("Overflow on mypid proportional")

        # componente derivativa
        if self.kd:
            out += ((error_ - self.prevError) * self.kd) / 2 ** self.shift_kd
            if not CheckSigned32(out):
                rpt_print("Overflow on mypid derivative")

        # componente integrale del campionamento precedente
        if self.ki:
            out += self.integral.getVal()
            if not CheckSigned32(out):
                rpt_print("Overflow on mypid integral")

        self.prev_error = error_

        if not CheckSigned32(out):
            rpt_print("Overflow on mypid output")

        # limitazione anti - windup con aggiornamento dell'errore integrale
        if out <= self.antiwindup_min:
            out = self.antiwindup_min
        elif out >= self.antiwindup_max:
            out = self.antiwindup_max
        else:
            self.integral.increment(error_ * self.ki, self.shift_ki, self.integral_limit)

        return out
