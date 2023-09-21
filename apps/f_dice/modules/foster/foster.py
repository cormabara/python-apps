# Stima della temperatura con Foster

import sys

from f_dice.lib.report import rpt_print, rpt_sep

from f_dice.modules.foster.constants import perc_err, power_w_2_wcu, current_lsb2A_theo, igbt_factor_theo, \
    igbt_offset_theo, igbt_w_to_deg_t, diode_factor_theo, diode_offset_theo, diode_w_to_deg_t, pwm_max_duty, \
    igbt_factor_real, diode_factor_real, curr_factor, diode_wcu_to_deg_r, igbt_wcu_to_deg_r, diode_offset_real, \
    igbt_offset_real
from f_dice.lib.tools import CheckIntOverflow


class DataFormat(int):
    data_theo_W = 0x0100
    data_theo_WCU = 0x0200
    data_real_WCU = 0x0400
    data_compare = 0x0800
    data_error = 0x1000
    data_real_deg = 0x2000
    data_theo_deg = 0x4000

    data_format_mask = 0xff00


class DataType(int):
    PIT = 0x0001
    PDT = 0x0002
    PIB = 0x0004
    PDB = 0x0008
    data_type_mask = 0x00ff


# This function take a fload, evaluate the rounding error to int, check the overflow and return
# the integer
def check_value(value_float_: float, print_):
    overflow = False
    if print_:
        if int(value_float_) != 0:
            err = perc_err(value_float_, int(value_float_))
        else:
            err = 0
        overflow = CheckIntOverflow(value_float_, 32)
        rpt_print("Op: err%(" + str(err) + ") overflow(" + str(overflow) + ")")

    if overflow == True:
        sys.exit(-2);

    return int(value_float_)


class PowerDato:

    def __init__(self):
        self.real = 0
        self.theo = 0
        self.theo_deg = 0
        self.real_deg = 0

    def get_value(self, format_):
        if format_ == DataFormat.data_theo_W:
            return self.theo
        elif format_ == DataFormat.data_theo_WCU:
            return power_w_2_wcu(self.theo)
        elif format_ == DataFormat.data_real_WCU:
            return self.real
        elif format_ == DataFormat.data_compare:
            return self.real - power_w_2_wcu(self.theo)
        elif format_ == DataFormat.data_error:
            return abs((self.real - (power_w_2_wcu(self.theo))) * 100 / (1 if self.real == 0 else self.real))
 
        elif format_ == DataFormat.data_real_deg:
            return self.real_deg
        elif format_ == DataFormat.data_theo_deg:
            return self.theo_deg
        return -1

    def set_value(self, format_, val_):
        if format_ == DataFormat.data_theo_W:
            self.theo = val_
        elif format_ == DataFormat.data_real_WCU:
            self.real = val_
        elif format_ == DataFormat.data_real_deg:
            self.real_deg = val_
        elif format_ == DataFormat.data_theo_deg:
            self.theo_deg = val_


class PowerSample:

    def __init__(self):
        self.pit = PowerDato()
        self.pib = PowerDato()
        self.pdt = PowerDato()
        self.pdb = PowerDato()

    def get_value(self, data_mode_):
        d_type = data_mode_ & DataType.data_type_mask
        d_format = data_mode_ & DataFormat.data_format_mask

        if d_type == DataType.PIT:
            return self.pit.get_value(d_format)
        elif d_type == DataType.PIB:
            return self.pib.get_value(d_format)
        elif d_type == DataType.PDT:
            return self.pdt.get_value(d_format)
        elif d_type == DataType.PDB:
            return self.pdb.get_value(d_format)
        return -1

    def set_value(self, data_mode_, val_):
        d_type = data_mode_ & DataType.data_type_mask
        d_format = data_mode_ & DataFormat.data_format_mask

        if d_type == DataType.PIT:
            self.pit.set_value(d_format, val_)
        elif d_type == DataType.PIB:
            self.pib.set_value(d_format, val_)
        elif d_type == DataType.PDT:
            self.pdt.set_value(d_format, val_)
        elif d_type == DataType.PDB:
            self.pdb.set_value(d_format, val_)


class PowerData:

    def __init__(self,do_print):
        self.current = None
        self.compare = None
        self.samples = 0
        self.power_samples = None
        self.sample_iter = None
        self.debug_print = do_print
        pass

    def CalcVectors(self, current_v_, compare_v_):
        size_v = [len(current_v_), len(compare_v_)]
        size = min(size_v)
        self.current = current_v_
        self.compare = compare_v_
        self.sample_iter = range(int(size))
        self.power_samples = [PowerSample() for i in self.sample_iter]
        self.samples = [i for i in self.sample_iter]
        for index in self.sample_iter:
            self.power_samples[index] = self.__calc_single(current_v_[index], compare_v_[index])

    def CalcSingle(self, current_, compare_):
        size = 1
        self.sample_iter = range(int(size))
        self.power_samples = [PowerSample() for i in self.sample_iter]
        self.samples = [i for i in self.sample_iter]
        for index in self.sample_iter:
            self.power_samples[index] = self.__calc_single(current_, compare_)
        return self.power_samples[0]

    def __calc_theoretical(self, sample: PowerSample, current_lsb_: float, compare_: float):
        """

        :param sample: container of data
        :param current_lsb_: current value in LSB
        :param compare_: compare value
        :return: none

        This function calculate the power as:
        power_t[W] = (current[A] * (compare/pwm_max_duty) * factor_t) + offset_t
              = (current_lsb_2_A_T(current_lsb_) * (compare/max_pwm_duty) * factor_t) + offset_t

        where factor_t and offset_t are constant calculated
        """

        # Conversion of current from lsb to Ampere
        current_A = current_lsb2A_theo(current_lsb_)
        mul_var = float(float(abs(current_A)) * float(compare_ / pwm_max_duty))
        mul_var_compl = float(abs(current_A)) * (1 - (compare_ / pwm_max_duty))

        if self.debug_print:
            rpt_sep()
            rpt_print("real factor and offset estimation")
            bkp = self.debug_print
            self.debug_print = False
            dbg_val = (mul_var_compl * igbt_factor_theo())
            dbg_val_compl = self.__value_convert(igbt_factor_real(), abs(current_lsb_), mul_var_compl)
            dbg_offs = igbt_offset_theo()
            self.debug_print = bkp
            rpt_print("factor is: " + str(dbg_val) + "( compl: " + str(dbg_val_compl) + ") - offset is: " + str(dbg_offs))

        if current_A > 0:
            val = (mul_var_compl * igbt_factor_theo()) + igbt_offset_theo()
            sample.set_value(DataType.PIT | DataFormat.data_theo_W, val)
            sample.set_value(DataType.PIT | DataFormat.data_theo_deg, igbt_w_to_deg_t(val))

            val = (mul_var * diode_factor_theo()) + diode_offset_theo()
            sample.set_value(DataType.PDB | DataFormat.data_theo_W, val)
            sample.set_value(DataType.PDB | DataFormat.data_theo_deg, diode_w_to_deg_t(val))

        else:
            val = (mul_var * igbt_factor_theo()) + igbt_offset_theo()
            sample.set_value(DataType.PIB | DataFormat.data_theo_W, val)
            sample.set_value(DataType.PIB | DataFormat.data_theo_deg, igbt_w_to_deg_t(val))

            val = (mul_var_compl * diode_factor_theo()) + diode_offset_theo()
            sample.set_value(DataType.PDT | DataFormat.data_theo_W, val)
            sample.set_value(DataType.PDT | DataFormat.data_theo_deg, diode_w_to_deg_t(val))

    # Funzione principale di conversione a rischio overflow, QUi ad ogi operazione faccio il test dell'overflow
    def __value_convert(self, dev_factor_: int, curr_: int, cmp_: int):
        '''

        :param dev_factor_:
        :param curr_:
        :param cmp_:
        :return:

        retval = curr_ * cmp_ * ( (dev_factor_ * CURR_FACTOR) / ( 1024 * 1000  ) )

        Dove:
            CURR_FACTOR variabile
            dev_factor_ variabile
            1/1000 = 131 >> 17
            1/1024 = >> 10

        Qui eseguiamo le operazioni una alla volta controllando overflow e l'errore in percentuale

        '''

        # Calcolo ( (curr_factor * dev_factor)  / 1000 ), questo calcolo è affidabile perchè curr_factor e dev_factor sono noti
        # ache se non costanti
        aux: float = (131 * float(curr_factor * dev_factor_)) / (1 << 17)
        aux = check_value(aux, self.debug_print)

        # moltiplico per la corrente
        aux *= curr_
        aux = check_value(aux, self.debug_print)

        # parzializzo la divisione per non perdere risoluzione
        aux /= (1 << 4)
        aux = check_value(aux, self.debug_print)

        aux *= cmp_
        aux = check_value(aux, self.debug_print)

        # parzializzo la divisione per non perdere risoluzione
        aux /= (1 << 6)
        aux = check_value(aux, self.debug_print)

        # ora confronto il valore clacolato a float globale con il risultato per
        # valutare l'errore di approssimazione complessivo
        if self.debug_print:
            aux_theo = (lsb2a_factor * dev_factor_ * curr_ * cmp_)
            rpt_print("aux: (" + str(aux) + ") - aux_theo(" + str(aux_theo) + ")")
            rpt_print("Value convert: err(" + str(perc_err( aux, aux_theo)) + ")")
        return int(aux)

    def __calc_real(self, sample: PowerSample, current_lsb_, compare_):
        """

        :param sample:
        :param current_lsb_:
        :param compare_:
        :return:

    	Power[WCu] = ((VCE_IGBT_V * Curr[A] * CompRate) * CUSTOM_FACTOR) + (DevOffset[W] * CUSTOM_FACTOR)

	    where:
	    CompRate = compare_/pwm_max_duty
	    DevOffset[W] = IGBT_E_W * pwm_frequency_hz

        So:

	    Power = (VCE_IGBT_V * Curr[A] * compare_ * CUSTOM_FACTOR)/pwm_max_duty + DevOffset[W]*CUSTOM_FACTOR
	    Power = (VCE_IGBT_V * Curr[A] * compare_ * CUSTOM_FACTOR)/pwm_max_duty
	            + (IGBT_E_W * pwm_frequency_hz)*CUSTOM_FACTOR

    	where:
	    PwmMaxDuty = CMP_RATE_BASE * shift_freq_factor
	    pwm_frequency_hz = PWM_BASE_FREQ_HZ / shift_freq_factor
	    Curr[A] = (current_lsb * CURR_FACTOR) / (1024 * 1000)

        if Power = Power1 + Power2

        Power1 = (VCE_IGBT_V * ((current_lsb * CURR_FACTOR) / (1024 * 1000)) * compare_ * CUSTOM_FACTOR)/ (CMP_RATE_BASE * shift_freq_factor)
        Power2 = (IGBT_E_W * PWM_BASE_FREQ_HZ * CUSTOM_FACTOR) / shift_freq_factor

        Power1 = (VCE_IGBT_V * current_lsb * CURR_FACTOR * compare_ * CUSTOM_FACTOR) / ( 1024 * 1000 * CMP_RATE_BASE * shift_freq_factor )
        Power2 = (IGBT_E_W * PWM_BASE_FREQ_HZ) / shift_freq_factor

	    Vars = compare_ * current_lsb

        Power1 = Vars * (VCE_IGBT_V * CURR_FACTOR * CUSTOM_FACTOR ) / ( 1024 * 1000 * CMP_RATE_BASE * shift_freq_factor )
        Power2 = (IGBT_E_W * PWM_BASE_FREQ_HZ * CUSTOM_FACTOR) / shift_freq_factor

        Power1 = Vars * ( (VCE_IGBT_V * CURR_FACTOR * CUSTOM_FACTOR) / ( 1024 * 1000 * CMP_RATE_BASE ) ) / shift_freq_factor
        Power2 = (IGBT_E_W * PWM_BASE_FREQ_HZ  * CUSTOM_FACTOR) / shift_freq_factor

        but igbt_factor_real = (VCE_IGBT_V * CUSTOM_FACTOR) / CMP_RATE_BASE
            igbt_offset_real = (IGBT_E_W * PWM_BASE_FREQ_HZ  * CUSTOM_FACTOR)

        Power1 = Vars * ( (igbt_factor_real * CURR_FACTOR) / ( 1024 * 1000) ) / shift_freq_factor )
        Power2 = igbt_offset_real / shift_freq_factor

        Power1 = value_convert(igbt_factor_real, current_lsb, compare_)  / shift_freq_factor )
        Power2 = igbt_offset_real / shift_freq_factor

        real = value_convert(igbt_factor_real, current_lsb, compare_) + igbt_offset_real

        dove real_2_theo(real): theo = (real/shift_freq_factor)/CUSTOM_FACTOR  """
        # rpt_print("REAL CALCULATION: current(" + str(current_lsb_) + ") - compare(" + str(compare_) + ")")
        mul_var = compare_
        mul_var_compl = pwm_max_duty - compare_

        if self.debug_print:
            rpt_sep()
            rpt_print("theoretical factor and offset estimation")
            bkp = self.debug_print
            self.debug_print = True
            dbg_val = self.__value_convert(igbt_factor_real(), abs(current_lsb_), mul_var)
            dbg_val_compl = self.__value_convert(igbt_factor_real(), abs(current_lsb_), mul_var_compl)
            dbg_offs = igbt_offset_real()
            self.debug_print = bkp
            rpt_print("factor is: " + str(dbg_val) + "(compl: " + str(dbg_val_compl) + ") - offset is: " + str(dbg_offs))

        if current_lsb_ > 0:
            val = self.__value_convert(igbt_factor_real(), abs(current_lsb_), mul_var_compl) + igbt_offset_real()
            sample.set_value(DataType.PIT | DataFormat.data_real_WCU, val)
            sample.set_value(DataType.PIT | DataFormat.data_real_deg, igbt_wcu_to_deg_r(val))

            val = self.__value_convert(diode_factor_real(), abs(current_lsb_), mul_var) + diode_offset_real()
            sample.set_value(DataType.PDB | DataFormat.data_real_WCU, val)
            sample.set_value(DataType.PDB | DataFormat.data_real_deg, diode_wcu_to_deg_r(val))
        else:
            val = self.__value_convert(igbt_factor_real(), abs(current_lsb_), mul_var) + igbt_offset_real()
            sample.set_value(DataType.PIB | DataFormat.data_real_WCU, val)
            sample.set_value(DataType.PIB | DataFormat.data_real_deg, igbt_wcu_to_deg_r(val))

            val = self.__value_convert(diode_factor_real(), abs(current_lsb_), mul_var_compl) + diode_offset_real()
            sample.set_value(DataType.PDT | DataFormat.data_real_WCU, val)
            sample.set_value(DataType.PDT | DataFormat.data_real_deg, diode_wcu_to_deg_r(val))

    def __calc_single(self, fixed_current_, fixed_compare_):
        rpt_sep()
        # rpt_print("Single calculation")
        mul_var = abs(current_lsb2A_theo(fixed_current_)) * fixed_compare_ / pwm_max_duty
        mul_var_compl = abs(current_lsb2A_theo(fixed_current_)) * (1 - (fixed_compare_ / pwm_max_duty))

        # rpt_print("current_A:\t " + str(current_lsb2A_theo(fixed_current_)))
        # rpt_print("mulvar:\t\t " + str(mul_var))
        # rpt_print("mulvar_c:\t " + str(mul_var_compl))

        sample = PowerSample()
        self.__calc_real(sample, fixed_current_, fixed_compare_)
        self.__calc_theoretical(sample, fixed_current_, fixed_compare_)
        return sample

    def get_current(self):
        return self.current

    def get_compare(self):
        return self.compare

    def get_values(self, which_data_):
        vector = [0 for i in self.sample_iter]
        for index in self.sample_iter:
            vector[index] = self.power_samples[index].get_value(which_data_)
        return vector

