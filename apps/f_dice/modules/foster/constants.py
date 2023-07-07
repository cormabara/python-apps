# @file File with all conversion factor and conversion functions

from mb_common_lib.report import rpt_print, rpt_print_d, rpt_sep
import math
from f_dice.lib.tools import divshx

ALICONV = "ALICONV"
ISD2 = "ISDPRO"

PLATFORM = ISD2

# fattore di conversione da lsb a mA (CURR_FACTOR/1024)
CURR_FACTOR_ISDPRO = 12845
CURR_FACTOR_ALICONV = 1536

Tau_IGBT_R = 0.04  # [s]
Tau_DIODE_R = 0.04  # [s]

if PLATFORM == ISD2:
    curr_factor = CURR_FACTOR_ISDPRO
    MAX_CURRENT_A = 250

    VCE_IGBT_V = 2.45  # Costante di tensione igbt [V]
    IGBT_EON_W = 14.10E-3  # Energia on [J]
    IGBT_EOFF_W = 26.40E-3  # energia off [J]

    V_DIODE_V = 2.42  # Costante di tensione del diodo [V]
    DIODE_EREC_W = 17E-3  # Energia dissipata dal diodo [W]

    RTH_IGBT_T = 0.14  # [K/W]
    RTH_DIODE_T = 0.2  # [K/W]
    # = 14/100 = mul (71)	 sh (9)	 err% (0.9486607142857237)
    def RTH_IGBT_R(w_):		
        return divshx((w_) * 71, 9)	 		
    # = 20/100 = mul (51)	 sh (8)	 err% (0.39062500000000555)
    def RTH_DIODE_R(w_):		
        return divshx((w_) * 51, 8)			

else:
    curr_factor = CURR_FACTOR_ALICONV
    MAX_CURRENT_A = 27
    
    VCE_IGBT_V = 1.6  # Costante di tensione igbt [V]
    IGBT_EON_W = 0.65E-3  # Energia on [J]
    IGBT_EOFF_W = 1.6E-3  # energia off [J]

    V_DIODE_V = 1.5  # Costante di tensione del diodo [V]
    DIODE_EREC_W = 0.83E-3  # Energia dissipata dal diodo [W]

    RTH_IGBT_T = 0.66 + 0.8  # [K/W]
    RTH_DIODE_T = 1 + 0.85  # [K/W]

    # = 1,46 = 146/100 mul (93)	 sh (6)	 err% (0.47089041095890166)
    def RTH_IGBT_R(w_):
        return divshx((w_) * 93, 6)

    # = 1,85 = 185/100 mul (59)	 sh (5)	 err% (0.3378378378378426)
    def RTH_DIODE_R(w_):		
        return divshx((w_) * 59, 5)			


# Dati di partenza dell'algoritmo descritto da Nick
ALT_CPU_FREQ  = 100000000
PWM_BASE_FREQ_HZ = 20000 # base frequency of the PWM

# Costanti energia prese dal datasheet
IGBT_E_W = (IGBT_EON_W + IGBT_EOFF_W)  # Energia dissipata da IGBT [W]

# Costanti di tensione

# Shift usato come moltiplicatore per evitare la perdita di risoluzione
CU_SHIFT = 16

# Frequency shift, variabile
FreqShift = 1  # shift of the base frequency da 100uS a 200uS shift = 1
shift_freq_factor = (1 << FreqShift)
CUSTOM_FACTOR = 1 << CU_SHIFT

CMP_RATE_BASE = int( (ALT_CPU_FREQ/PWM_BASE_FREQ_HZ)/2)  # reference value for the compare
pwm_frequency_hz = int(ALT_CPU_FREQ/PWM_BASE_FREQ_HZ) >> FreqShift      # [hz]
pwm_period_uS = (1/pwm_frequency_hz)*(1E6)                                  # periodo del pwm in uS
pwm_max_duty = CMP_RATE_BASE << FreqShift




def perc_err(val1_ : float, val2_: float):
    val = val1_ - val2_
    val = abs(val)
    if val1_ != 0:
        val = val / val1_
    elif val2_ != 0:
        val = val / val2_
    val = val * 100
    return val





#Function for the calculation theroical and real constants

# This is the factor for the thorical calculation [V]
def igbt_factor_theo():
    return VCE_IGBT_V


# Calculate factor for the real calculation [V << CUST_SHIFT]
def igbt_factor_real():
    return int( (VCE_IGBT_V * CUSTOM_FACTOR) / CMP_RATE_BASE)


# Offset calculation [W] (Eon+Eoff)*f  @225A, 600V
def igbt_offset_theo():
    return (IGBT_EON_W + IGBT_EOFF_W) * pwm_frequency_hz
    #return 0


# Offset calculation [W << CUST_SHIFT]
def igbt_offset_real():
    return int((IGBT_EON_W + IGBT_EOFF_W) * CUSTOM_FACTOR * PWM_BASE_FREQ_HZ)


def diode_factor_theo():
    return V_DIODE_V


def diode_factor_real():
    return int((V_DIODE_V * CUSTOM_FACTOR) / CMP_RATE_BASE)


# Offset calculation [W]
def diode_offset_theo():
    return DIODE_EREC_W * pwm_frequency_hz
    #return 0

# Offset calculation [W << CUST_SHIFT]
def diode_offset_real():
    return int(DIODE_EREC_W * CUSTOM_FACTOR * PWM_BASE_FREQ_HZ)
    #return 0


# Fattori di conversione tra watt e custom_watt
conv_w2wcu = CUSTOM_FACTOR * shift_freq_factor
conv_wcu2w = 1 / (CUSTOM_FACTOR * shift_freq_factor) 

def power_wcu_2_w(real_):
    return real_ * conv_wcu2w


def power_w_2_wcu(theo_):
    return theo_ * conv_w2wcu



# Fattore di conversione da lsm_ ad ampere
lsb2a_factor = curr_factor / (1024 * 1000)
a2lsb_factor = (1024 * 1000) / curr_factor


MAX_CURRENT_LSB = int(MAX_CURRENT_A * a2lsb_factor)
MIN_CURRENT_LSB = -int(MAX_CURRENT_A * a2lsb_factor)

# Conversion current from lsb to A for the theorical calculation
def current_lsb2A_theo(lsb_: float):
    return lsb_ * lsb2a_factor

def current_A2lsb_theo(A_: float):
    return A_ * a2lsb_factor




# foster model
Tau_IGBT_T = 0.04  # [s]
Tau_DIODE_T = 0.04  # [s]

F_SAMPLE_HZ = 1E3;  # [HZ] Sampling 1ms
# banda passante
igbt_lp_ft_t = 1 / (Tau_IGBT_T * (2 * math.pi))  # [Hz]
diode_lp_ft_t = 1 / (Tau_DIODE_T * (2 * math.pi))  # [Hz]



# dove :
# Tau_DIODE_T * (2*math.pi) = 0,2512
# quindi:
# igbt_lp_ft_r [Hz] = 1 / 0,2512 = 10000 / 2512 [Hz]
# quindi
# igbt_lp_ft_r [mHz] = (10000000 / 2512) [mHz] = 3980,89 [mHz]

igbt_lp_fcut_r = 4000  # [mHz]  -> 4HZ -> 0,25 sec
diode_lp_fcut_r = 4000  # [mHz]	 -> 4Hz -> 0,25 sec

# Frequenza di campionamento deve essere almeno 10 volte quidni 40Hz
# Dato che la frequenza di campinamento deve essere almeno 1/10 della frequenza di taglio possiamo unare anche 100Hz per la fequenza di campionamento
# in modo da eseguire il camionamento ogni 10ms il che ci permette di andare sotto main
f_sample_r = 40  # [Hz] -> Ogni 25ms




def igbt_w_to_deg_t(w_):
    return RTH_IGBT_T * w_

def diode_w_to_deg_t(w_):
    return RTH_DIODE_T * w_

def igbt_wcu_to_deg_r(wcu_):
    return RTH_IGBT_R(power_wcu_2_w(wcu_))

def diode_wcu_to_deg_r(wcu_):
    return RTH_DIODE_R(power_wcu_2_w(wcu_))


EDGE_DEGREE = 50


def rpt_print_constants():
    rpt_sep()
    rpt_print("IGBT CONSTANT")
    rpt_print("VCE_IGBT_V [V]: " + str(VCE_IGBT_V))
    rpt_print("IGBT_E_W   [W]: " + str(IGBT_E_W))

    rpt_print("\nTheorical calculation\n")
    rpt_print_d("igbt_factor_t [V] ", igbt_factor_theo())
    rpt_print_d("igtb_offset_t [W]", igbt_offset_theo())

    rpt_print("\nCustom calculation\n")
    rpt_print_d("igbt_factor_r [VCU] ", igbt_factor_real())
    rpt_print_d("igtb_offset_r [WCU]", igbt_offset_real())

    # qui ricalcolo il fattore reale ma partendo la teorico ed eseguendo tutte le operazioni senza arrotondamento a INT
    # in questo modo vedo l'errore commesso nel calcolo reale ripetto a quello teorico
    factor_r_theorical = (igbt_factor_theo() * CUSTOM_FACTOR) / CMP_RATE_BASE
    error_perc = perc_err(factor_r_theorical, igbt_factor_real())
    rpt_print("igbt_factor_error (" + str(igbt_factor_real()) + ") - (" + str(factor_r_theorical) + "): " + str(
        error_perc) + "[%]")

    rpt_sep()
    rpt_print("DIODE CONSTANT")
    rpt_print("V_DIODE_V [V]: " + str(V_DIODE_V))
    rpt_print("DIODE_EREC_W   [W]: " + str(DIODE_EREC_W))

    rpt_print("\nTheorical calculation with factor in volt and offset in Watt\n")
    rpt_print_d("diode_factor_t [V] ", diode_factor_theo())
    rpt_print_d("diode_offset_t [W]", diode_offset_theo())

    rpt_print("\nCustom calculation\n")
    rpt_print_d("diode_factor_r [VCU] ", diode_factor_real())
    rpt_print_d("diode_offset_r [WCU]", diode_offset_real())

    # qui ricalcolo il fattore reale ma partendo la teorico ed eseguendo tutte le operazioni senza arrotondamento a INT
    # in questo modo vedo l'errore commesso nel calcolo reale ripetto a quello teorico
    factor_r_theorical = (diode_factor_theo() * CUSTOM_FACTOR) / CMP_RATE_BASE
    error_perc = perc_err(factor_r_theorical, diode_factor_real())
    rpt_print("diode_factor_error (" + str(diode_factor_real()) + ") - (" + str(factor_r_theorical) + "): " + str(
        error_perc) + "[%]")

def print_start_data():
    rpt_sep()
    rpt_print("PLATFORM: " + PLATFORM)
    rpt_print_d("CMP_RATE_BASE", CMP_RATE_BASE)

    rpt_print("\nCURRENT DATA")
    rpt_print_d("lsb2a_factor",lsb2a_factor)
    rpt_print_d("a2lsb_factor",a2lsb_factor)    
    rpt_print_d("MAX_CURRENT [A]",MAX_CURRENT_A)
    rpt_print_d("MAX_CURRENT [LSB]",MAX_CURRENT_LSB)
    rpt_print_d("MIN_CURRENT [LSB]",MIN_CURRENT_LSB)
    
    rpt_print_d("FreqShift", FreqShift)
    rpt_print_d("curr_factor",curr_factor)
    rpt_print_d("pwm_max_duty", pwm_max_duty)
    rpt_print_d("pwm_frequency_hz", pwm_frequency_hz)
    rpt_print_d("pwm_period_uS", pwm_period_uS)
    rpt_print_d("pwm_period_uS", pwm_period_uS)
    
    rpt_print_d("RTH_IGBT_T", RTH_IGBT_T)
    rpt_print_d("RTH_DIODE_T", RTH_DIODE_T)
    
    rpt_print_constants()
