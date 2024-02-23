""" This module is the input stage of the system
    Qui facciamo la gestione degli zerocross e anche la gestione del PLL sulle fasi """
from collections import deque
from enum import Enum

from my_errors import SysErr
from my_timers import SysTimer
from report import MyReport
from tools import CnfAfe, SinForm


class SigmaDelta:

    def __init__(self):
        pass

    def execute(self,in_1_,in_2_):
        return in_2_ - in_1_


class LineIn:

    ZEROCROSS_SMPL = CnfAfe().PERIOD_IN_SAMPLES / 2  # Samples tra uno zerocross e l'altro
    ZEROCROSS_SMPL_TOL = 5  # Tolleranza di scostamento dal valore

    MIN_ZC = (ZEROCROSS_SMPL - (
                ZEROCROSS_SMPL * ZEROCROSS_SMPL_TOL / 100))  # Minimo per iltest della singola forma d'onda
    MAX_ZC = (ZEROCROSS_SMPL + (
                ZEROCROSS_SMPL * ZEROCROSS_SMPL_TOL / 100))  # Massimo per il test della singola forma d'onda

    ZC_CROSS_LIMIT = (ZEROCROSS_SMPL * 2 / 3)
    MIN_CROSS_LIM = (ZC_CROSS_LIMIT - (ZC_CROSS_LIMIT * ZEROCROSS_SMPL_TOL / 100))
    MAX_CROSS_LIM = (ZC_CROSS_LIMIT + (ZC_CROSS_LIMIT * ZEROCROSS_SMPL_TOL / 100))

    ZC_CROSS_WRONGSEQ = (ZEROCROSS_SMPL * 1 / 3)
    MIN_CROSS_WRONGSEQ = (ZC_CROSS_WRONGSEQ - (
                ZC_CROSS_WRONGSEQ * ZEROCROSS_SMPL_TOL / 100))  # Valore minimo per la wrong direction
    MAX_CROSS_WRONGSEQ = (ZC_CROSS_WRONGSEQ + (
                ZC_CROSS_WRONGSEQ * ZEROCROSS_SMPL_TOL / 100))  # Valore massimo per la wrong direction

    class FailMasks(Enum):
        fail_mask_none = 0x00
        fail_mask_RS_missing = 0x01
        fail_mask_ST_missing = 0x02
        fail_mask_RSST_missing = 0x04
        fail_mask_RSST_wrong = 0x08


    class ZeroCross:

        def __init__(self):
            self.zc_cnt = 0
            self.zc_val = 0
            self.zc_trig = 0
            self.zc_buff = 0
            self.zc_fail = 0

        def reset(self):
            self.zc_cnt = 0
            self.zc_val = 0
            self.zc_buff = 0
            self.zc_trig = -1
            self.zc_fail = 0

        def _sign_changed(self, in1_, in2_):
            return in1_ * in2_ < 0

        def sample_zc(self, in_):
            retval = False
            if self._sign_changed(in_, self.zc_buff):
                self.zc_val = self.zc_cnt
                self.zc_cnt = 0
                self.zc_trig += 1
                retval = True
            elif self.zc_trig >= 0:
                self.zc_trig = 0

            self.zc_buff = in_  # Aggiorno i due buffer per il test del cambio di segno
            return retval
        def check_zc(self):
            """ Questa funzione riceve in ingresso il valore del contatore tra due zerocross e ne verifica
                la validita' controllando che sia nel range """
            if self.zc_val < LineIn.MIN_ZC:
                return SysErr().set_alarm(-1, "zerocross under minimum:" + str(self.zc_val))
            # Controllo se zerocross rs oltre il massimo
            elif self.zc_val > LineIn.MAX_ZC:
                return SysErr().set_alarm(-1, "zerocross over maximum: " + str(self.zc_val))
            return 0

    def __init__(self):
        self.zerocross_rs = self.ZeroCross()
        self.zerocross_st = self.ZeroCross()
        self.zc_RS_ST_cnt = 0
        self.zc_ST_RS_cnt = 0
        self.zc_RS_ST_val = 0
        self.zc_ST_RS_val = 0
        self.zc_RS_trig_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.zc_ST_trig_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.fail_phases_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)


    def reset(self):
        self.zerocross_rs.reset()
        self.zerocross_st.reset()
        self.zc_RS_ST_cnt = 0
        self.zc_ST_RS_cnt = 0
        self.zc_RS_ST_val = 0
        self.zc_ST_RS_val = 0

    def _check_sequence(self):
        """ Controllo la sequenza delle fasi per capire la direzione: Se siamo sotto il minimo 1 o sopra il massimo 2
            allora anomalia dei due segnali
            Se invece siamo nel range accettabile ma siamo fuori dalla finestra 1 allora sequenza rovescia """
        if self.zc_ST_RS_val < self.MIN_CROSS_WRONGSEQ or self.zc_ST_RS_val > self.MAX_CROSS_LIM:
            SysErr().set_alarm(-1,"cross phases ST-RS out of time",)
        elif self.zc_ST_RS_val > self.MAX_CROSS_WRONGSEQ:
            SysErr().set_alarm(-1,"cross phases ST-RS wrong direction",)

    def sample_and_check(self, in_rs_, in_st_):
        self.zerocross_rs.zc_cnt += 1
        self.zerocross_st.zc_cnt += 1
        self.zc_RS_ST_cnt += 1
        self.zc_ST_RS_cnt += 1

        if self.zerocross_rs.sample_zc(in_rs_):
            self.zc_ST_RS_val = self.zc_ST_RS_cnt
            self.zc_RS_ST_cnt = 0

        if self.zerocross_st.sample_zc(in_st_):
            self.zc_RS_ST_val = self.zc_RS_ST_cnt
            self.zc_ST_RS_cnt = 0

        if (self.zerocross_rs.zc_trig >= 0) and (self.zerocross_st.zc_trig >= 0):
            if (self.zerocross_rs.zc_trig > 0) or (self.zerocross_st.zc_trig > 0):

                if self.zerocross_rs.zc_trig > 0:
                    self.zerocross_rs.check_zc()
                    self._check_sequence()

                if self.zerocross_st.zc_trig > 0:
                    self.zerocross_st.check_zc()

        self.plot_sample()

    def plot_sample(self):
        self.zc_RS_trig_v.append(int(self.zerocross_rs.zc_trig) * CnfAfe().AMPLITUDE)
        self.zc_ST_trig_v.append(int(self.zerocross_st.zc_trig) * CnfAfe().AMPLITUDE)

    def report_debug(self):
        MyReport().rpt_print("RS: {0} - ST: {0}"
                             .format(str(self.zerocross_rs.zc_val))
                             .format(str(self.zerocross_st.zc_val)))
        MyReport().rpt_print("ST to RS: {0}".format(str(self.zc_ST_RS_val)))
        MyReport().rpt_print("RS to ST: {0}".format(str(self.zc_RS_ST_val)))


class VMains:

    def __init__(self):


        # Primo stadio i convertitori sigma delta
        self.in_st = None
        self.in_rs = None
        self.sg_rs = SigmaDelta()
        self.sg_st = SigmaDelta()
        #Quindi gestione degli zerocross
        self.linein = LineIn()

        self. in_RS_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.in_ST_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    def start(self):
        self.linein.reset()

    def execute(self, ph_r_, ph_s_, ph_t_):
        self.in_rs = self.sg_rs.execute(ph_r_,ph_s_)
        self.in_st = self.sg_st.execute(ph_s_,ph_t_)
        self.linein.sample_and_check(self.in_rs,self.in_st)
        self.plot_sample()

    def plot_sample(self):
        self.in_RS_v.append(self.in_rs)
        self.in_ST_v.append(self.in_st)
        pass
