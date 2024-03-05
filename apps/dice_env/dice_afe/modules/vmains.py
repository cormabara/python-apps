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
from tools import CnfAfe


class VMains:
    """ Stadio di ingresso di AFE.
        - Prende in ingresso le 3 linee di fase, ricava le due uscite dei sigma delta e quindi ricalcola le tre fasi
        - Sulle due uscite dei sigma delta esegue la check zerocross
        - Sulle tre fasi ricalcolate esegue il pll per determinare theta e omegas """

    def __init__(self):

        # Primo stadio i convertitori sigma delta
        self.metodo = 3
        self.in_T = None
        self.in_S = None
        self.in_R = None
        self.in_rs = None
        self.in_ts = None

        # Questi solo per calcoli intermedi
        self.in_rt = None
        self.in_tr = None
        self.in_st = None

        # Costruisco i due sigma delta
        self.sg_rs = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)
        self.sg_ts = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE, CnfAfe().SIGMADELTA_RESOLUTION)

        # Instantiate the input stage
        self.linein = LineIn()
        # Instantiate the PLL on phases
        self.pll = PhasesPll(CnfAfe().RealMode, CnfAfe().SAMPLE_FREQUENCY_HZ, CnfAfe().WIN_DEEP)
        # Vettori solo per il plot
        self.in_RS_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_TS_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_R_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_S_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_T_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    def start(self):
        self.linein.reset()

    def execute(self, ph_r_, ph_s_, ph_t_):
        # Passo le fasi di ingresso nei sigma delta in modo da avere le grandezze in LSB
        # Ricalcolo le fasi di ingresso dai due sigma delta
        """
        Partiamo dai due segnali del sigma delta
        TS = in_TS (T-S)
        RS = in_RS (R-S)
        
        # Applicando kirchoff calcolo anche il terzo segnale triangolo
        SR + TS + RT = 0
        RT = -SR - TS = RS -TS
        TR            = TS - RS """

        self.in_rs = self.sg_rs.calculate(ph_r_, ph_s_)
        self.in_ts = self.sg_ts.calculate(ph_t_, ph_s_)
        self.in_rt = self.in_rs - self.in_ts
        self.in_tr = -self.in_rt
        self.in_st = -self.in_ts

        """ Applicando kirchoff ai singoli vertici        
        # Ora calcolo di nuovo le tre fasi di ingresso
        R + RT - SR = 0     -> R = SR - RT = - RS - RT 
        S + SR - TS = 0     -> S = TS - SR = TS + RS
        T + TS - RT = 0     -> T = RT - TS = RT - TS 
        """
        if self.metodo == 1:
            # Ora calcolo di nuovo le tre fasi di ingresso, calcolandole così mi  ritrovo le tre fasi in uscita sfasate
            # di 180° rispetto a quelle di ingresso
            self.in_R = -self.in_rs - self.in_rt
            self.in_S = self.in_ts + self.in_rs
            self.in_T = self.in_rt - self.in_ts

        elif self.metodo == 2:
            """ secondo metodo 
            R = SR - RT   = (-RS) - ( RS -TS )   = TS - 2*RS 
            S = -SR - TS                         = RS - TS
            T = RT - TS   = (RS -TS) - TS        = RS - 2*TS    """
            self.in_R = (self.in_ts - 2 * self.in_rs) / 3
            self.in_S = (self.in_rs - self.in_ts) / 3
            self.in_T = (self.in_rs - 2 * self.in_ts) / 3
        else:
            """ Trezo metodo (NICOLA)"""
            self.in_R = (self.in_rs - self.in_tr) / 3
            self.in_S = (self.in_st - self.in_rs) / 3
            self.in_T = (self.in_tr - self.in_st) / 3

        self.linein.sample_and_check(self.in_rs, self.in_ts)
        self.pll.calculate(self.in_R, self.in_S, self.in_T)
        self.plot_sample()

    def get_theta_out(self):
        """ Recupera il valore del theta """
        # Qui compenso il ritardo di 180° inserito durante la conversione triangolo stella
        return (self.pll.get_theta_custom() + self.pll.THETA_CUSTOM_RANGE) % self.pll.THETA_CUSTOM_RANGE

    def get_theta_out_range(self):
        """ Recupera il range del theta come da formule trigo di DICE """
        return self.pll.THETA_CUSTOM_RANGE

    def plot_sample(self):
        """ Aggiorno i vettori """

        # Uscite sigma delta
        self.in_RS_v.append(self.in_rs)
        self.in_TS_v.append(self.in_ts)

        # Fasi ricalcolate dai sigma delta
        self.in_R_v.append(self.in_R)
        self.in_S_v.append(self.in_S)
        self.in_T_v.append(self.in_T)
        pass
