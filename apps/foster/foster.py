# Stima della temperatura con Foster

from report import rpt_print_d, rpt_print, rpt_sep
from constants import MAX_CURRENT_LSB, MIN_CURRENT_LSB, current_lsb2A_theo
from constants import igbt_factor_real, igbt_offset_real,diode_factor_real,diode_offset_real
from constants import igbt_factor_theo, igbt_offset_theo,diode_factor_theo,diode_offset_theo
from constants import pwm_max_duty, curr_factor,perc_err
from constants import power_theo_2_real,power_real_2_theo
from common import CheckIntOverflow


class DataFormat(int):
    data_theo_W = 0x0100
    data_theo_WCU = 0x0200
    data_real_WCU = 0x0400
    theo_real_error_perc = 0x0800
    data_format_mask = 0xff00


class DataType(int):
    PIT = 0x0001
    PDT = 0x0002
    PIB = 0x0004
    PDB = 0x0008
    data_type_mask = 0x00ff


class PowerDato:

    def __init__(self):
        self.real = 0
        self.theo = 0

    def get_value(self, format_):
        if format_ == DataFormat.data_theo_W:
            return self.theo
        elif format_ == DataFormat.data_theo_WCU:
            return power_theo_2_real(self.theo)
        elif format_ == DataFormat.data_real_WCU:
            return self.real
        elif format_ == DataFormat.theo_real_error_perc:
            return abs((self.real - (power_theo_2_real(self.theo))) * 100 / (1 if self.real == 0 else self.real))
        elif format_ == DataFormat.theo_deg:
            return self.theo
        return -1

    def set_value(self, format_, val_):
        if format_ == DataFormat.data_theo_W:
            self.theo = val_
        elif format_ == DataFormat.data_real_WCU:
            self.real = val_


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

    def check_overflow(self):
        if (self.pit.real > 0x70000000 or self.pdt.real > 0x70000000 or
                self.pib.real > 0x70000000 or self.pdb.real > 0x70000000):
            rpt_print("Overflow")
            return True


class PowerData:
    current_iter: range
    power_sample: []  # Samples con iterazione su compare
    power_sample_curr: []  # Samples con iterazione su corrente

    def __init__(self,single_):
        self.single = single_

        # Const for the custom unity calculation
        self.errors_pit = None
        self.errors_pib = None
        self.errors_pdt = None
        self.errors_pdb = None
        self.compare_range = None
        self.compare_iter = range(pwm_max_duty)

        self.current_delta = 100;
        self.current_iter = range(int(((MAX_CURRENT_LSB - MIN_CURRENT_LSB)/self.current_delta)-1))
        self.current_range = [0 for i in self.current_iter]
        for cc in self.current_iter:
            val = MIN_CURRENT_LSB + cc*self.current_delta
            self.current_range[cc] = val
            if 0 >= val > -100:
                val = -100
            elif 0 <= val < 100:
                val = 100

        self.power_sample_curr = [PowerSample() for i in self.current_iter]

    def GetCurrentValues(self) :
        return self.current_range

    def calc_theoretical(self, sample: PowerSample, current_lsb_ : float, compare_: float):
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
        mul_var_compl = float(abs(current_A) * (1 - (compare_ / pwm_max_duty)))

        if current_A > 0:
            sample.set_value(DataType.PIT | DataFormat.data_theo_W,
                             (mul_var * igbt_factor_theo()) + igbt_offset_theo())
            sample.set_value(DataType.PDB | DataFormat.data_theo_W,
                             (mul_var_compl * diode_factor_theo()) + diode_offset_theo())
        else:
            sample.set_value(DataType.PIB | DataFormat.data_theo_W,
                             (mul_var_compl * igbt_factor_theo()) + igbt_offset_theo())
            sample.set_value(DataType.PDT | DataFormat.data_theo_W,
                             (mul_var * diode_factor_theo()) + igbt_offset_theo())

    # This function take a fload, evaluate the rounding error to int, check the overflow and return
    # the integer
    def check_value(self, valfloat_: float, print_):
        if print_:
            err = perc_err(valfloat_, int(valfloat_))
            overflow = CheckIntOverflow(valfloat_, 32)
            rpt_print("Op: err%(" + str(err) + ") overflow(" + str(overflow) + ")")

        return int(valfloat_)


    # Funzione principale di conversione a rischio overflow, QUi ad ogi operazione faccio il test dell'overflow
    def value_convert(self, dev_factor_: int, curr_: int, cmp_: int):
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
        aux = self.check_value(aux, self.single)

        # moltiplico per la corrente
        aux *= curr_;
        aux = self.check_value(aux, self.single)

        # parzializzo la divisione per non perdere risoluzione
        aux /= (1 << 4)
        aux = self.check_value(aux, self.single)

        aux *= cmp_
        aux = self.check_value(aux, self.single)

        # parzializzo la divisione per non perdere risoluzione
        aux /= (1 << 6)
        aux = self.check_value(aux, self.single)


        # ora confronto il valore clacolato a float globale con il risultato per
        # valutare l'errore di approssimazione complessivo
        if self.single:
            aux_theo = (curr_factor * dev_factor_ * curr_ * cmp_) / (1000 * 1024)
            rpt_print("End: err(" + str(perc_err( aux,aux_theo)) + ")")
            rpt_print("aux: (" + str(aux) + ") - aux_theo(" + str(aux_theo) + ")")

        return int(aux)

    def value_convert_c(self, dev_factor_, curr_factor_, curr_lsb_,cmp_):
        aux = (131 * curr_factor_ * dev_factor_) >> 17
        aux = (aux * curr_lsb_) >> 4
        aux = (aux * cmp_) >> 6
        return aux;

    def calc_real(self, sample: PowerSample, current_lsb_, compare_):
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
	    pwm_frequency_hz = SYSTMR_BASE_FREQ_HZ / shift_freq_factor
	    Curr[A] = (current_lsb * CURR_FACTOR) / (1024 * 1000)

        if Power = Power1 + Power2

        Power1 = (VCE_IGBT_V * ((current_lsb * CURR_FACTOR) / (1024 * 1000)) * compare_ * CUSTOM_FACTOR)/ (CMP_RATE_BASE * shift_freq_factor)
        Power2 = (IGBT_E_W * SYSTMR_BASE_FREQ_HZ * CUSTOM_FACTOR) / shift_freq_factor

        Power1 = (VCE_IGBT_V * current_lsb * CURR_FACTOR * compare_ * CUSTOM_FACTOR) / ( 1024 * 1000 * CMP_RATE_BASE * shift_freq_factor )
        Power2 = (IGBT_E_W * SYSTMR_BASE_FREQ_HZ) / shift_freq_factor

	    Vars = compare_ * current_lsb

        Power1 = Vars * (VCE_IGBT_V * CURR_FACTOR * CUSTOM_FACTOR ) / ( 1024 * 1000 * CMP_RATE_BASE * shift_freq_factor )
        Power2 = (IGBT_E_W * SYSTMR_BASE_FREQ_HZ * CUSTOM_FACTOR) / shift_freq_factor

        Power1 = Vars * ( (VCE_IGBT_V * CURR_FACTOR * CUSTOM_FACTOR) / ( 1024 * 1000 * CMP_RATE_BASE ) ) / shift_freq_factor
        Power2 = (IGBT_E_W * SYSTMR_BASE_FREQ_HZ  * CUSTOM_FACTOR) / shift_freq_factor

        but igbt_factor_real = (VCE_IGBT_V * CUSTOM_FACTOR) / CMP_RATE_BASE
            igbt_offset_real = (IGBT_E_W * SYSTMR_BASE_FREQ_HZ  * CUSTOM_FACTOR)

        Power1 = Vars * ( (igbt_factor_real * CURR_FACTOR) / ( 1024 * 1000) ) / shift_freq_factor )
        Power2 = igbt_offset_real / shift_freq_factor

        Power1 = value_convert(igbt_factor_real, current_lsb, compare_)  / shift_freq_factor )
        Power2 = igbt_offset_real / shift_freq_factor

        real = value_convert(igbt_factor_real, current_lsb, compare_) + igbt_offset_real

        dove real_2_theo(real): theo = (real/shift_freq_factor)/CUSTOM_FACTOR  """

        if current_lsb_ > 0:
            if self.single:
                rpt_sep()
                rpt_print("PIT Calculation")
            val = self.value_convert(igbt_factor_real(), abs(current_lsb_), compare_)
            sample.set_value(DataType.PIT | DataFormat.data_real_WCU, val + igbt_offset_real())

            if self.single:
                rpt_sep()
                rpt_print("PDB Calculation")
            val = self.value_convert(diode_factor_real(), abs(current_lsb_), pwm_max_duty - compare_)
            sample.set_value(DataType.PDB | DataFormat.data_real_WCU, val + diode_offset_real())

        else:
            if self.single:
                rpt_print("PIB Calculation")
            val = self.value_convert(igbt_factor_real(), abs(current_lsb_), pwm_max_duty - compare_)
            sample.set_value(DataType.PIB | DataFormat.data_real_WCU, val + igbt_offset_real())

            if self.single:
                rpt_print("PDT Calculation")
            val = self.value_convert(diode_factor_real(), abs(current_lsb_), compare_)
            sample.set_value(DataType.PDT | DataFormat.data_real_WCU, val + diode_offset_real())

    def calc_iter_current(self, compare_):
        for cc in self.current_iter:
            val = MIN_CURRENT_LSB + (cc*self.current_delta)
            if 0 >= val > -100:
                val = -100
            elif 0 <= val < 100:
                val = 100

            self.calc_theoretical(self.power_sample_curr[cc], self.current_range[cc], compare_)
            self.calc_real(self.power_sample_curr[cc], self.current_range[cc], compare_)

    def calc_single(self, fixed_current_, fixed_compare_):
        rpt_sep()
        rpt_print("Single calculation")
        mul_var = abs(current_lsb2A_theo(fixed_current_)) * fixed_compare_ / pwm_max_duty
        mul_var_compl = abs(current_lsb2A_theo(fixed_current_)) * (1 - (fixed_compare_ / pwm_max_duty))

        rpt_print("current_A:\t " + str(current_lsb2A_theo(fixed_current_)))
        rpt_print("mulvar:\t\t " + str(mul_var))
        rpt_print("mulvar_c:\t " + str(mul_var_compl))

        if fixed_current_ != 0 and fixed_compare_ != 0:
            sample = PowerSample()
            self.calc_real(sample, fixed_current_, fixed_compare_)
            self.calc_theoretical(sample, fixed_current_, fixed_compare_)
            return sample

        return None

    def get_samples(self, data_mode_):
        tmp = [0 for cc in self.current_iter]
        for ii in self.current_iter:
            tmp[ii] = self.power_sample_curr[ii].get_value(data_mode_)
        return tmp

    def check_overflow(self):
        tmp = [0 for cc in self.current_iter]
        for ii in self.current_iter:
            if self.power_sample_curr[ii].check_overflow():
                rpt_print("overflow on index" + str(ii))
                return

    def print_data_curr(self):
        rpt_print("\n\nestimation of power consumption for the complete current range")
        rpt_print("PIT")
        rpt_print_d("min T [W]", min(self.get_samples(DataType.PIT | DataFormat.data_theo_W)))
        rpt_print_d("max T [W]", max(self.get_samples(DataType.PIT | DataFormat.data_theo_W)))
        rpt_print_d("min T [WCU]", min(self.get_samples(DataType.PIT | DataFormat.data_theo_WCU)))
        rpt_print_d("max T [WCU]", max(self.get_samples(DataType.PIT | DataFormat.data_theo_WCU)))
        rpt_print_d("min R  ", min(self.get_samples(DataType.PIT | DataFormat.data_real_WCU)))
        rpt_print_d("max R  ", max(self.get_samples(DataType.PIT | DataFormat.data_real_WCU)))
        rpt_print_d("err% min  ", min(self.get_samples(DataType.PIT | DataFormat.theo_real_error_perc)))
        rpt_print_d("err% max  ", max(self.get_samples(DataType.PIT | DataFormat.theo_real_error_perc)))
        rpt_print("PIB")
        rpt_print_d("min T [W]", min(self.get_samples(DataType.PIB | DataFormat.data_theo_W)))
        rpt_print_d("max T [W]", max(self.get_samples(DataType.PIB | DataFormat.data_theo_W)))
        rpt_print_d("min T [WCU]", min(self.get_samples(DataType.PIB | DataFormat.data_theo_WCU)))
        rpt_print_d("max T [WCU]", max(self.get_samples(DataType.PIB | DataFormat.data_theo_WCU)))
        rpt_print_d("min R  ", min(self.get_samples(DataType.PIB | DataFormat.data_real_WCU)))
        rpt_print_d("max R  ", max(self.get_samples(DataType.PIB | DataFormat.data_real_WCU)))
        rpt_print_d("err% min  ", min(self.get_samples(DataType.PIB | DataFormat.theo_real_error_perc)))
        rpt_print_d("err% max  ", max(self.get_samples(DataType.PIB | DataFormat.theo_real_error_perc)))
        rpt_print("PDT")
        rpt_print_d("min T [W]", min(self.get_samples(DataType.PDT | DataFormat.data_theo_W)))
        rpt_print_d("max T [W]", max(self.get_samples(DataType.PDT | DataFormat.data_theo_W)))
        rpt_print_d("min T [WCU]", min(self.get_samples(DataType.PDT | DataFormat.data_theo_WCU)))
        rpt_print_d("max T [WCU]", max(self.get_samples(DataType.PDT | DataFormat.data_theo_WCU)))
        rpt_print_d("min R  ", min(self.get_samples(DataType.PDT | DataFormat.data_real_WCU)))
        rpt_print_d("max R  ", max(self.get_samples(DataType.PDT | DataFormat.data_real_WCU)))
        rpt_print_d("err% min  ", min(self.get_samples(DataType.PDT | DataFormat.theo_real_error_perc)))
        rpt_print_d("err% max  ", max(self.get_samples(DataType.PDT | DataFormat.theo_real_error_perc)))
        rpt_print("PDB")
        rpt_print_d("min T [W]", min(self.get_samples(DataType.PDB | DataFormat.data_theo_W)))
        rpt_print_d("max T [W]", max(self.get_samples(DataType.PDB | DataFormat.data_theo_W)))
        rpt_print_d("min T [WCU]", min(self.get_samples(DataType.PDB | DataFormat.data_theo_WCU)))
        rpt_print_d("max T [WCU]", max(self.get_samples(DataType.PDB | DataFormat.data_theo_WCU)))
        rpt_print_d("min R  ", min(self.get_samples(DataType.PDB | DataFormat.data_real_WCU)))
        rpt_print_d("max R  ", max(self.get_samples(DataType.PDB | DataFormat.data_real_WCU)))
        rpt_print_d("err% min  ", min(self.get_samples(DataType.PDB | DataFormat.theo_real_error_perc)))
        rpt_print_d("err% max  ", max(self.get_samples(DataType.PDB | DataFormat.theo_real_error_perc)))
