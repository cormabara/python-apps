""" Class for a generic PID
"""

from mb_common_lib.types import S32_MAX, S32_MIN


def saturate_out_of_range(val_, min_, max_):
    if val_ < min_:
        val_ = min_
    elif val_ > max_:
        val_ = max_
    return val_


# supporto per componente integrale dei PID
class XIntegral:
    val: int
    fractional: int

    def __init(self):
        self.val = 0
        self.fractional = 0

    def preset(self, val_: int):
        self.val = val_
        self.fractional = 0

    def increment(self, step_: int, shift_: int, limit_: int):
        self.fractional += step_
        # si usa l'approssimazione per rendere simmetrica l'operazione (valori positivi/negativi)
        increment = int(self.fractional / 2 ** shift_)
        self.fractional -= (increment << shift_)
        # calcolo del valore
        self.val = saturate_out_of_range((self.val + increment), -limit_, +limit_)
        return self.val

    def reduce(self, shift_):
        self.val -= int(self.val / 2 ** shift_)


class DicePid:
    prev_error: int  # valore precedente dell'errore
    integral: XIntegral  # contributo integrale
    kp: int  # coefficiente proporzionale
    kd: int  # coefficiente derivativo
    ki: int  # coefficiente integrale
    shift_kp: int  # shift componente proporzionale (per avere pesi frazionari)
    shift_kd: int  # shift componente derivativa (per avere pesi frazionari)
    shift_ki: int  # shift componente integrale (per avere pesi frazionari)
    antiwindup_max: int  # anti-windup, limite massimo
    antiwindup_min: int  # anti-windup, limite minimo
    integral_limit: int  # valore limite dell'integrale (positivo = max, negativo = min)

    def __init__(self):
        self.kp = 0
        self.kd = 0
        self.ki = 0
        self.antiwindup_max = S32_MAX
        self.antiwindup_min = S32_MIN
        self.integral = XIntegral()
        self.reset()

    def setProportional(self, kp_, shift_kp_):
        self.kp = kp_
        self.shift_kp = shift_kp_

    def setIntegral(self, kd_, shift_kd_):
        self.kd = kd_
        self.shift_kd = shift_kd_

    def setDerivative(self, kd_, shift_kd_):
        self.kd = kd_
        self.shift_kd = shift_kd_

    def reset(self):
        self.prev_error = 0
        self.integral.preset(0)

    def outputPI(self, error_: int):  # error_ = reference - real
        """ componente proporzionale + integrale istante precedente """
        out = 0
        if self.kp:
            out = int(error_ * self.kp) / 2 ** self.shift_kp
        if self.ki:
            out += self.integral.val / 2 ** self.shift_ki

        # limitazione anti - windup
        if out <= self.antiwindup_min:
            out = self.antiwindup_min
        elif out >= self.antiwindup_max:
            out = self.antiwindup_max
        else:
            # aggiornamento componente integrale
            if self.ki:
                self.integral.increment((error_ * self.ki), self.shift_ki, self.integral_limit)
        return out

    def outputPID(self, error_: int):  # error_ = reference - real
        # componente proporzionale
        out = 0
        if self.kp:
            out = (error_ * self.kp) / 2 ** self.shift_kp
        # componente derivativa
        if self.kd:
            out += ((error_ - self.prev_error) * self.kd) / 2 ** self.shift_kd
        # componente integrale
        if self.ki:
            out += self.integral.increment(error_ * self.ki, self.shift_ki, self.integral_limit)

        self.prev_error = error_

        # limitazione anti - windup
        if out <= self.antiwindup_min:
            out = self.antiwindup_min
            # diminuisce l'effetto integrale perche' sottraggo una quantita' con lo stesso segno (1/32)
            if self.ki:
                self.integral.reduce(self.shift_ki)
        elif out >= self.antiwindup_max:
            out = self.antiwindup_max
            # diminuisce l'effetto integrale perche' sottraggo una quantita' con lo stesso segno (1/32)
            if self.ki:
                self.integral.reduce(self.shift_ki)
        return out
