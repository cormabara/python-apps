""" This module is the input stage of the system
    Qui facciamo la gestione degli zerocross e anche la gestione del PLL sulle fasi

    TS(ii) = -mainsST(ii);
    RT(ii)= mainsRT(ii);
    SR(ii)= -TS(ii)-RT(ii);

    R(ii)= (SR(ii)-RT(ii))/3;
    S(ii) = (TS(ii)-SR(ii))/3;
    T(ii) = (RT(ii)-TS(ii))/3;
"""
from collections import deque
from enum import Enum

from apps.f_dice.modules.phases_pll import PhasesPll
from linein import LineIn
from my_errors import SysErr
from my_sigmadelta import SigmaDelta
from my_timers import SysTimer
from report import MyReport
from tools import CnfAfe, SinForm


class VMains:

    def __init__(self):


        # Primo stadio i convertitori sigma delta
        self.in_st = None
        self.in_rt = None
        self.sg_st = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE,CnfAfe().SIGMADELTA_RESOLUTION)
        self.sg_rt = SigmaDelta(CnfAfe().IN_MAXAMPLITUDE,CnfAfe().SIGMADELTA_RESOLUTION)

        # Instantiate the input stage
        self.linein = LineIn()
        # Instantiate the PLL on phases
        self.pll = PhasesPll(CnfAfe().RealMode, CnfAfe().SAMPLE_FREQUENCY_HZ,CnfAfe().WIN_DEEP)

        self.in_ST_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_RT_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    def start(self):
        self.linein.reset()

    def execute(self, ph_r_, ph_s_, ph_t_):
        # Passo le fasi di ingresso nei sigma delta in modo da avere le grandezze in LSB
        self.in_st = self.sg_st.calculate(ph_s_,ph_t_)
        self.in_rt = self.sg_rt.calculate(ph_r_,ph_t_)

        self.linein.sample_and_check(self.in_st,self.in_rt)

        # Ricalcolo le fasi di ingresso dai due sigma delta
        """in_TS = -self.in_st
        in_RT = self.in_rt
        # Applicando kirchoff calcolo anche il terzo segnale triangolo
        in_SR = -in_TS - in_RT;

        # Ora calcolo di nuovo le tre fasi di ingresso
        in_R = (in_SR - in_RT) / 3
        in_S = (in_TS - in_SR) / 3
        in_T = (in_RT - in_TS) / 3"""
        # Ora calcolo di nuovo le tre fasi di ingresso, calcolandole così mi  ritrovo le tre fasi in uscita sfasate
        # di 180° rispetto a quelle di ingresso
        in_R = (self.in_st - 2 * self.in_rt)/3
        in_S = (self.in_rt - 2 * self.in_st)/3
        in_T = (self.in_rt + self.in_st)/3

        self.pll.calculate(in_R, in_S, in_T)
        self.plot_sample()

    def get_theta_out(self):
        # Qui compenso il ritardo di 180° inserito durante la conversione triangolo stella
        return (self.pll.get_theta_custom() + self.pll.THETA_CUSTOM_RANGE) % self.pll.THETA_CUSTOM_RANGE

    def get_theta_out_range(self):
        return self.pll.THETA_CUSTOM_RANGE


    def plot_sample(self):
        self.in_ST_v.append(self.in_st)
        self.in_RT_v.append(self.in_rt)
        pass

