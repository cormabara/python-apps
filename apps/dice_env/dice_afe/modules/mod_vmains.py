""" This module is the input stage of the system
    Qui facciamo la gestione degli zerocross e anche la gestione del PLL sulle fasi
    - Partiamo dai due ingressi dei sigma delta
    - Sui due ingressi così come sono facciamo il check della zerocross
    - Ricaviamo le 3 fasi singole e le diamo in pasto al PLL per determinare:
        - Theta
        - Omega
        - Vac_rms
"""
from collections import deque

from devices.phases_pll import PhasesPll
from devices.linein import LineIn
from my_sigmadelta import SigmaDelta
from afe_config import CnfAfe, board_set_alarm, Alarms
from my_types import drverr_dt


class VMains:
    """ Stadio di ingresso di AFE.
        - Prende in ingresso le 3 linee di fase, ricava le due uscite dei sigma delta e quindi ricalcola le tre fasi
        - Sulle due uscite dei sigma delta esegue la check zerocross
        - Sulle tre fasi ricalcolate esegue il pll per determinare theta e omegas """

    def __init__(self,rm_=False):
        self.rm = rm_
        # Primo stadio i convertitori sigma delta
        self.metodo = 3
        self.in_T_lsb = None
        self.in_S_lsb = None
        self.in_R_lsb = None

        # Costruisco i due sigma delta
        self.sg_rs = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)
        self.sg_ts = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)

        # Instantiate the input stage
        self.linein = LineIn()
        # Instantiate the PLL on phases
        self.pll = PhasesPll(CnfAfe().RealMode, CnfAfe().SAMPLE_FREQUENCY_HZ, CnfAfe().WIN_DEEP)
        # Vettori solo per il plot
        self.in_R_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_S_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_T_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    def init(self):
        pass

    def start(self):
        pass

    def start(self):
        self.linein.reset()

    def calculate_phases(self, in_rs_lsb_, in_ts_lsb_):
        """ Questa funzione riceve in ingresso le due uscite del sigma delta e ritorna
        le 3 fasi ricostruite
        Applicando kirchoff calcolo anche il terzo segnale triangolo
        rs + st + tr = 0 """
        in_sr_lsb = -in_rs_lsb_
        in_st_lsb = -in_ts_lsb_
        in_tr_lsb = - in_rs_lsb_ - in_st_lsb

        if self.metodo == 1:
            # Ora calcolo di nuovo le tre fasi di ingresso, calcolandole così mi  ritrovo le tre fasi in uscita sfasate
            # di 180° rispetto a quelle di ingresso
            self.in_R_lsb = in_sr_lsb - in_rs_lsb_
            self.in_S_lsb = in_ts_lsb_ + in_rs_lsb_
            self.in_T_lsb = in_rs_lsb_ - in_ts_lsb_

        elif self.metodo == 2:
            """ secondo metodo
            R = SR - RT   = (-RS) - ( RS -TS )   = TS - 2*RS
            S = -SR - TS                         = RS - TS
            T = RT - TS   = (RS -TS) - TS        = RS - 2*TS    """
            self.in_R_lsb = (in_ts_lsb_ - 2 * in_rs_lsb_) / 3
            self.in_S_lsb = (in_rs_lsb_ - in_ts_lsb_) / 3
            self.in_T_lsb = (in_rs_lsb_ - 2 * in_ts_lsb_) / 3
        else:
            """ Trezo metodo (NICOLA)"""
            self.in_R_lsb = (in_rs_lsb_ - in_tr_lsb) / 3
            self.in_S_lsb = (in_st_lsb - in_rs_lsb_) / 3
            self.in_T_lsb = (in_tr_lsb - in_st_lsb) / 3

    def handle(self, in_rs_lsb_, in_ts_lsb_):
        self.calculate_phases(in_rs_lsb_, in_ts_lsb_)
        self.linein.sample_and_check(in_rs_lsb_, in_ts_lsb_)
        self.pll.calculate(self.in_R_lsb, self.in_S_lsb, self.in_T_lsb)
        self.plot_sample()


    def background(self):
        pass

    def get_theta_out(self):
        """ Recupera il valore del theta """
        # Qui compenso il ritardo di 180° inserito durante la conversione triangolo stella
        return (self.pll.get_theta_custom() + self.pll.THETA_CUSTOM_RANGE) % self.pll.THETA_CUSTOM_RANGE

    def get_theta_out_range(self):
        """ Recupera il range del theta come da formule trigo di DICE """
        return self.pll.THETA_CUSTOM_RANGE

    def plot_sample(self):
        """ Aggiorno i vettori """


        # Fasi ricalcolate dai sigma delta
        self.in_R_v.append(self.in_R_lsb)
        self.in_S_v.append(self.in_S_lsb)
        self.in_T_v.append(self.in_T_lsb)

    def get_vac(self):
        return self.pll.get_vac()

    def check_input(self) -> drverr_dt:
        if not self.pll.is_locked():
            return board_set_alarm(Alarms.vmains_al_pllNotLocked,"Pll is not correctly locked")

        vac = self.pll.get_vac()
        if vac > CnfAfe().MAX_VAC_LSB or vac < CnfAfe().MIN_VAC_LSB:
            return board_set_alarm(Alarms.vmains_al_vacNotOk, "La Vac letta è fuori dai limiti accettabili")

        return 0