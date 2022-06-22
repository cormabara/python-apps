# Stima della temperatura con Foster


from report import rpt_print_d, rpt_print
from conversions import LSB2A_CURR_FACTOR, A2LSB_CURR_FACTOR
from conversions import current_lsb_2_A

# Dati di partenza dell'algoritmo descritto da Nick

SYSTMR_BASE_FREQ_HZ = 10000  # base frequency of the pwm
CMP_RATE_BASE = 5000  # reference value for the compare

# Costanti prese dal datasheet
IGBT_EON_W = 1.430E-3  # Energia on [W]
IGBT_EOFF_W = 26.40E-3  # energia off [W]

DIODE_EREC_W = 17E-3  # Energia diodo [W]

VCE_IGBT_V = 2.45  # Tensione riferimento IGBT
V_DIODE_V = 2.42;  # [V] @250A dc

# Shift usato come moltiplicatore per evitare la perdita di risoluzione
CU_SHIFT = 16

# Frequency shift, variabile
FreqShift = 1  # shift of the base frequency da 100uS a 200uS shift = 1

pwm_frequency_hz = SYSTMR_BASE_FREQ_HZ >> FreqShift
pwm_max_duty = CMP_RATE_BASE << FreqShift


class ConstIgbt:

    def __init__(self):
        self.igbt_factor_t: float = 0
        self.igbt_factor_r: int = 0

        self.igbt_offset_t: float = 0
        self.igbt_offset_r: int = 0

        self.igbt_vce_cv = VCE_IGBT_V * (1 << CU_SHIFT)      # igbt voltage factor [cu]
        self.igbt_e_cw = (IGBT_EON_W + IGBT_EOFF_W) * (1 << CU_SHIFT)
        self.calc_igbt_factor()
        self.calc_igbt_offset()

    def calc_igbt_factor(self):
        # Theorical value for the factor
        self.igbt_factor_t = VCE_IGBT_V / pwm_max_duty
        self.igbt_factor_r = int(self.igbt_vce_cv / CMP_RATE_BASE)

    def calc_igbt_offset(self):
        self.igbt_offset_t = (IGBT_EON_W + IGBT_EOFF_W) * pwm_frequency_hz  # [W] (Eon+Eoff)*f  @225A, 600V
        self.igbt_offset_r = int(self.igbt_e_cw * SYSTMR_BASE_FREQ_HZ)


class ConstDiode:

    def __init__(self):
        self.diode_factor_t: float = 0
        self.diode_factor_r: int = 0

        self.diode_offset_t: float = 0
        self.diode_offset_r: int = 0

        self.v_diode_cv = V_DIODE_V * (1 << CU_SHIFT)
        self.diode_erec_cw = DIODE_EREC_W * (1 << CU_SHIFT)

        self.calc_diode_factor()
        self.calc_diode_offset()

    def calc_diode_factor(self):
        self.diode_factor_t = V_DIODE_V / pwm_max_duty
        self.diode_factor_r = int(self.v_diode_cv / CMP_RATE_BASE)

    def calc_diode_offset(self):
        self.diode_offset_t = DIODE_EREC_W * pwm_frequency_hz
        self.diode_offset_r = int(self.diode_erec_cw * SYSTMR_BASE_FREQ_HZ)


class PowerSample:

    def __init__(self):
        self.pit_r = 0
        self.pib_r = 0
        self.pdt_r = 0
        self.pdb_r = 0
        self.pit_t = 0
        self.pib_t = 0
        self.pdt_t = 0
        self.pdb_t = 0

    def get_error_pit(self):
        return self.pit_t - self.pit_r

    def get_error_perc_pit(self):
        return self.get_error_pit() * 100 / self.pit_r

    def check_limit_pit(self):
        if self.pit_r > 0x7fffffff:
            return False;


class PowerData:

    igbt_const: ConstIgbt
    diode_const: ConstDiode

    power_sample: []

    def __init__(self):

        max_compare = pwm_max_duty

        self.compare_iter = range(max_compare)

        # Const for the custom unity calculation
        self.igbt_vce_cv: int = 0
        self.v_diode_cv: int = 0

        self.igbt_factor_cv: int = 0        # Fattore di tensione igbt in custom voltage (shifted)
        self.igbt_offset_cw: int = 0        # Fattore di potenza igbt in custom watt (shifted)
        self.diode_factor_cv: int = 0       # Fattore di tensione diodo in custom voltage (shifted)
        self.diode_offset_cw: int = 0       # Fattore di potenza diodo in custom watt (shifted)

        self.power_sample = [PowerSample() for i in self.compare_iter]

        # Variables for the Watt calculation
        self.igtb_offset_w = 0
        self.diode_offset_w = 0
        self.igbt_factor_v = 0
        self.diode_factor_v = 0

        myiter = self.compare_iter
        self.compare_range = [0 for i in myiter]
        self.pit_error_v = [0 for i in myiter]
        self.pit_errorperc_v = [0 for i in myiter]

        self.pib_W = [0 for i in myiter]
        self.pib_cu = [0 for i in myiter]
        self.pib_error_v = [0 for i in myiter]
        self.pib_errorperc_v = [0 for i in myiter]

        self.pdt_W = [0 for i in myiter]
        self.pdt_cu = [0 for i in myiter]
        self.pdt_error_v = [0 for i in myiter]
        self.pdt_errorperc_v = [0 for i in myiter]

        self.pdb_W = [0 for i in myiter]
        self.pdb_cu = [0 for i in myiter]
        self.pdb_error_v = [0 for i in myiter]
        self.pdb_errorperc_v = [0 for i in myiter]

        self.Const_W()
        self.Const_Cu()

        self.igbt_const = ConstIgbt()
        self.diode_const = ConstDiode()


    # Calculate variables using theorical calculation (floating)
    def Const_W(self):

        rpt_print("\nVariables FOR THE WATT CALCULATION\n")

        self.igbt_factor_v = VCE_IGBT_V / pwm_max_duty
        rpt_print_d("igbt_factor_v [V] ", self.igbt_factor_v)

        self.diode_factor_v = V_DIODE_V / pwm_max_duty
        rpt_print_d("diode_factor_v [V] ", self.diode_factor_v)

        self.igtb_offset_w = (IGBT_EON_W + IGBT_EOFF_W) * pwm_frequency_hz  # [W] (Eon+Eoff)*f  @225A, 600V
        rpt_print_d("igtb_offset_w ", self.igtb_offset_w)

        self.diode_offset_w = DIODE_EREC_W * pwm_frequency_hz
        rpt_print_d("diode_offset_w", self.diode_offset_w)

    # Calculate all constants in custom unity
    def Const_Cu(self):

        rpt_print("\nCONST FOR THE CU CALCULATION (shift = " + str(CU_SHIFT) + "\n")

        self.igbt_vce_cv = VCE_IGBT_V * (1 << CU_SHIFT)      # igbt voltage factor [cu]
        # igbt_const_cv = vce_igbt_cv/cmp_rate
        # igbt_const_cv = vce_igbt_cv/ (cmp_rate_base << FreqShift)
        self.igbt_factor_cv = int(self.igbt_vce_cv / CMP_RATE_BASE)
        aux_igbt_factor_cv = self.igbt_factor_cv / (1 << FreqShift)
        rpt_print_d("vce_igbt_cv", self.igbt_vce_cv)
        rpt_print_d("power_data.igbt_factor_cv", self.igbt_factor_cv)
        rpt_print_d("igbt factor [cv]", aux_igbt_factor_cv)
        rpt_print_d("igbt factor [cv->v]", aux_igbt_factor_cv / (1 << CU_SHIFT))

        rpt_print("")

        self.v_diode_cv = V_DIODE_V * (1 << CU_SHIFT)
        self.diode_factor_cv = int(self.v_diode_cv / CMP_RATE_BASE)
        aux_diode_factor_cv = self.diode_factor_cv / (1 << FreqShift)
        rpt_print_d("V_DIODE_CV", self.v_diode_cv)
        rpt_print_d("power_data.DIODE_FACTOR_CV", self.diode_factor_cv)
        rpt_print_d("diode factor [cv]", aux_diode_factor_cv)
        rpt_print_d("diode factor [cv->v]", aux_diode_factor_cv / (1 << CU_SHIFT))

        rpt_print("")

        self.igbt_e_cw = (IGBT_EON_W + IGBT_EOFF_W) * (1 << CU_SHIFT)
        # igbt_offset_cw = IGBT_E_W * pwm_frequency_hz
        #                = IGBT_E_W * (SYSTMR_BASE_FREQ_HZ >> FreqShift)
        self.igbt_offset_cw = int(self.igbt_e_cw * SYSTMR_BASE_FREQ_HZ)
        aux_igbt_offset_cw = self.igbt_offset_cw / (1 << FreqShift)
        rpt_print_d("igbt_e_cw", self.igbt_e_cw)
        rpt_print_d("power_data.IGBT_OFFSET_CW", self.igbt_offset_cw)
        rpt_print_d("igbt_offset_cw", aux_igbt_offset_cw)
        rpt_print_d("igbt_offset_cw [cw->w]", aux_igbt_offset_cw / (1 << CU_SHIFT))

        rpt_print("")

        self.diode_erec_cw = DIODE_EREC_W * (1 << CU_SHIFT)
        self.diode_offset_cw = int(self.diode_erec_cw * SYSTMR_BASE_FREQ_HZ)
        aux_diode_offset_cw = self.diode_offset_cw / (1 << FreqShift)
        rpt_print_d("diode_erec_cw", self.diode_erec_cw)
        rpt_print_d("power_data.DIODE_OFFSET_CW", self.diode_offset_cw)
        rpt_print_d("idiode_offset_cw", aux_diode_offset_cw)
        rpt_print_d("diode_offset_cw [cw->w]", aux_diode_offset_cw / (1 << CU_SHIFT))
        rpt_print("")
        rpt_print("LSB2A_CURR_FACTOR: " + str(LSB2A_CURR_FACTOR) + "\n")
        rpt_print("A2LSB_CURR_FACTOR: " + str(A2LSB_CURR_FACTOR) + "\n")

    def calc_theoretical(self, sample: PowerSample, current_A_, compare_):
        """ Funzione che calcola le componenti in WATT parendo da corrente in [A]
            eseguo il calcolo in Watt, nel fare il calcolo aggiungo anche lo shift di CU_SHIFT per avere
            dati commparabili """
        mul_var = current_A_ * compare_
        mul_var_1 = current_A_ * (pwm_max_duty - compare_)

        if current_A_ > 0:
            sample.pit_t = (mul_var * self.igbt_factor_v + self.igtb_offset_w) * (1 << CU_SHIFT)
            sample.pdb_t = (mul_var_1 * self.diode_factor_v + self.diode_offset_w) * (1 << CU_SHIFT)
        else:
            sample.pib_t = (mul_var_1 * self.igbt_factor_v + self.igtb_offset_w) * (1 << CU_SHIFT)
            sample.pdt_t = (mul_var * self.diode_factor_v + self.diode_offset_w) * (1 << CU_SHIFT)

    def calc_real(self, sample: PowerSample, current_lsb_, compare_):
        """ eseguo il calcolo in Custom Unit
            usiamo la corrente in lsb quindi restiamo in credito di una moltiplica per JUNCT_CURR_FACTOR """
        curr_A = current_lsb_ * LSB2A_CURR_FACTOR
        # se mul_var = curr_A * compare_
        mul_var_p1 = current_lsb_ * LSB2A_CURR_FACTOR * compare_
        mul_var = (current_lsb_ * compare_) * LSB2A_CURR_FACTOR
        mul_var_compl = current_lsb_ * LSB2A_CURR_FACTOR * (pwm_max_duty - compare_)

        if current_lsb_ > 0:
            sample.pit_r = (int(self.igbt_factor_cv * mul_var) >> FreqShift) + (
                    int(self.igbt_offset_cw) >> FreqShift)
            sample.pdb_r = (int(self.diode_factor_cv * mul_var_compl) >> FreqShift) + (
                    int(self.diode_offset_cw) >> FreqShift)
        else:
            sample.pib_r = (int(self.igbt_factor_cv * mul_var_compl) >> FreqShift) + (
                    int(self.igbt_offset_cw) >> FreqShift)
            sample.pdt_r = (int(self.diode_factor_cv * mul_var) >> FreqShift) + (
                    int(self.diode_offset_cw) >> FreqShift)

    def iter_compare_calc(self, current_):

        rpt_print("\n\nVALUES for 0 to " + str(self.compare_iter) + "\n\n")

        for cc in self.compare_iter:
            self.compare_range[cc] = cc
            self.calc_theoretical(self.power_sample[cc], current_lsb_2_A(current_), cc)
            self.calc_real(self.power_sample[cc], current_, cc)
            self.pit_error_v[cc] = (self.power_sample[cc].pit_t - self.power_sample[cc].pit_r)
            self.pit_errorperc_v[cc] = self.pit_error_v[cc] * 100 / self.power_sample[cc].pit_r

            if self.power_sample[cc].pit_r > 0x7fffffff:
                rpt_print("ERROR: the value exceed maximum value from index: " + str(cc) + "\n")
                break

    def theo_samples_pit(self):
        tmp = []
        for ii in self.power_sample:
            tmp.append(ii.pit_t)
        return tmp

    def real_samples_pit(self):
        tmp = []
        for ii in self.power_sample:
            tmp.append(ii.pit_r)
        return tmp

    def error_perc_pit(self):
        tmp = []
        for ii in self.power_sample:
            tmp.append(ii.get_error_perc_pit())
        return tmp


power_data: PowerData
