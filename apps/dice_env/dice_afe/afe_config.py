import math
from collections import deque
from enum import IntEnum

from DmDictionary import DmDictionary
from my_sigmadelta import SigmaDelta
from my_types import drverr_dt
from report import MyReport
from tools import SingletonMeta


class Alarms(IntEnum):
    afe_al_init = 1
    afe_al_vbusNotStable = 2
    afe_al_inputNotOk = 3
    vmains_al_pllNotLocked = 4
    vmains_al_vacNotOk = 5


class Board(metaclass=SingletonMeta):

    def __init__(self):
        pass

    def set_alarm(self):
        pass


def board_set_alarm(err_, str_) -> drverr_dt:
    MyReport().rpt_error(err_, str_)
    Board().set_alarm()
    return err_


class CnfAfe(metaclass=SingletonMeta):
    WIN_DEEP = 1000  # Deep of the display window
    INPUT_FREQ_HZ = 50
    INPUT_OMEGA_RAD = 2 * math.pi * INPUT_FREQ_HZ
    INPUT_PERIOD_S = 1 / 50  # Periodo del segnale di ingresso (50Hz)
    INPUT_PERIOD_mS = INPUT_PERIOD_S * 1000  # Periodo del segnale di ingresso (50Hz)
    INPUT_PERIOD_uS = INPUT_PERIOD_mS * 1000  # Periodo del segnale di ingresso (50Hz)

    SYSTMR_FREQ_HZ = 10000
    SAMPLE_FREQUENCY_HZ = SYSTMR_FREQ_HZ
    SAMPLE_TIME_uS = 100  # Freuenza di campionamento sotto irq
    SAMPLE_TIME_mS = 1000 / SAMPLE_TIME_uS
    PERIOD_IN_SAMPLES = INPUT_PERIOD_uS / SAMPLE_TIME_uS  # Sinusoide completa in sample
    TRIGO_THETA_RANGE = 2 * math.pi

    AMPLITUDE = 200
    IN_MAXAMPLITUDE = 500
    SIGMADELTA_RESOLUTION = 12
    MAX_SIGMADELTA_VAL = 2**SIGMADELTA_RESOLUTION
    MAIN_LOOP_TIME_MS = 100
    MAIN_TIME_100uS = MAIN_LOOP_TIME_MS / SAMPLE_TIME_mS
    RealMode = False

    MAX_VAC_LSB = 2 ** SIGMADELTA_RESOLUTION - 1
    MIN_VAC_LSB = 10

    DICTIONARY_FILENAME = "/home/marco/lavori/python/data/dice_afe_dictionary.xml"

    def __init__(self):
        self.dictionary = DmDictionary()
        self.dictionary.from_xml(self.DICTIONARY_FILENAME)

    def dict_get_par(self, name_):
        do = self.dictionary.find_do_by_name(name_)
        if do:
            MyReport().rpt_print("The default value of " + str(do.mux) + " is: " + str(do.default))
            return do.value
        else:
            MyReport().rpt_print("cannot find DO: " + str(name_))
            return 0

    def display_range(self):
        return range(0, self.WIN_DEEP)


class AfeSignals(metaclass=SingletonMeta):
    """ Questa classe adibita alla generazione dei vari segnali di ingresso del sistema """

    theta_step_custom = CnfAfe().TRIGO_THETA_RANGE * (CnfAfe().INPUT_FREQ_HZ / CnfAfe().SAMPLE_FREQUENCY_HZ)
    Fpga_Vbus_fbk_lsb = 500

    ph3 = None
    ph2 = None
    ph1 = None
    theta_in_custom3 = None
    theta_in_custom2 = None
    theta_in_custom1 = None
    theta_in_custom = 0
    offset1 = offset2 = offset3 = 0

    # Questi solo per calcoli intermedi
    metodo = 3
    in_rs_lsb = None
    in_ts_lsb = None

    sg_rs = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)
    sg_ts = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)

    ph1_v = deque(CnfAfe().display_range(), maxlen=CnfAfe().WIN_DEEP)
    ph2_v = deque(CnfAfe().display_range(), maxlen=CnfAfe().WIN_DEEP)
    ph3_v = deque(CnfAfe().display_range(), maxlen=CnfAfe().WIN_DEEP)
    plot_in_rs = deque(CnfAfe().display_range(), maxlen=CnfAfe().WIN_DEEP)
    plot_in_ts = deque(CnfAfe().display_range(), maxlen=CnfAfe().WIN_DEEP)

    def __init__(self):
        pass

    def generate_phases_in(self):
        """ Questa funzione genera lo stimolo in ingresso 3 fasi di ampiezza AMPLITUDE sfasate di 120°
            e genera anche l'uscita dei due sigma delta. IN uscita abbiamo le due differenziali espresse in LSB """
        self.theta_in_custom = (self.theta_in_custom + self.theta_step_custom) % CnfAfe().TRIGO_THETA_RANGE
        self.theta_in_custom1 = self.theta_in_custom + self.offset1
        self.theta_in_custom2 = self.theta_in_custom + self.offset2
        self.theta_in_custom3 = self.theta_in_custom + self.offset3

        self.ph1 = CnfAfe().AMPLITUDE * math.sin(self.theta_in_custom1)
        self.ph2 = CnfAfe().AMPLITUDE * math.sin(self.theta_in_custom2 - ((2 * math.pi) / 3))
        self.ph3 = CnfAfe().AMPLITUDE * math.sin(self.theta_in_custom3 - ((4 * math.pi) / 3))

        ph_r = self.ph1
        ph_s = self.ph2
        ph_t = self.ph3

        # Generazione delle due uscite del sigma delta
        self.in_rs_lsb = self.sg_rs.calculate(ph_r, ph_s)
        self.in_ts_lsb = self.sg_ts.calculate(ph_t, ph_s)

        self.plot_sample()

    def plot_sample(self):
        # Aggiungo i campioni delle tre forme di ingresso
        self.ph1_v.append(self.ph1)
        self.ph2_v.append(self.ph2)
        self.ph3_v.append(self.ph3)

        # Uscite sigma delta
        self.plot_in_rs.append(self.in_rs_lsb)
        self.plot_in_ts.append(self.in_ts_lsb)

