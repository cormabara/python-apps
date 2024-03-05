from collections import deque
from enum import Enum

from my_errors import SysErr
from report import MyReport
from tools import CnfAfe


class LineIn:
    """ Input module class definition.
        This module hadles the three phases input stage. The real input of this stage is:
        - INPUT1: sigma-delta(phaseR - phaseT)
        - INPUT2: sigma-delta(phaseS - phaseT) """

    ZEROCROSS_SMPL = CnfAfe().PERIOD_IN_SAMPLES / 2  # Samples tra uno zerocross e l'altro
    ZEROCROSS_SMPL_TOL = 5  # Tolleranza di scostamento dal valore

    # Questo è l'intervallo utile per la corretta fase di ingresso (testiamo il singolo segnale)
    MIN_ZC = (ZEROCROSS_SMPL - (
                ZEROCROSS_SMPL * ZEROCROSS_SMPL_TOL / 100))  # Minimo per iltest della singola forma d'onda
    MAX_ZC = (ZEROCROSS_SMPL + (
                ZEROCROSS_SMPL * ZEROCROSS_SMPL_TOL / 100))  # Massimo per il test della singola forma d'onda

    # Questo è l'intervallo utile per la distanza dei due zerocross
    ZC_CROSS_LIMIT = (ZEROCROSS_SMPL * 1 / 3)
    MIN_CROSS_LIM = (ZC_CROSS_LIMIT - (ZC_CROSS_LIMIT * ZEROCROSS_SMPL_TOL / 100))
    MAX_CROSS_LIM = (ZC_CROSS_LIMIT + (ZC_CROSS_LIMIT * ZEROCROSS_SMPL_TOL / 100))

    ZC_CROSS_WRONGSEQ = (ZEROCROSS_SMPL * 2 / 3)
    MIN_CROSS_WRONGSEQ = (ZC_CROSS_WRONGSEQ - (
                ZC_CROSS_WRONGSEQ * ZEROCROSS_SMPL_TOL / 100))  # Valore minimo per la wrong direction
    MAX_CROSS_WRONGSEQ = (ZC_CROSS_WRONGSEQ + (
                ZC_CROSS_WRONGSEQ * ZEROCROSS_SMPL_TOL / 100))  # Valore massimo per la wrong direction

    class ZeroCross:
        """ Class to make the check of a single zerocross on a single sigma-delta signal """
        def __init__(self):
            self.zc_cnt = 0         # Tick counter for zero cross
            self.zc_val = 0         # Value of the tick counter
            self.zc_trig = 0        # Trigger flag for zero cross
            self.zc_buff = 0        # Buffer value for input singla

        def reset(self):
            self.zc_cnt = 0
            self.zc_val = 0
            self.zc_buff = 0
            self.zc_trig = -1

        def _sign_changed(self, in1_, in2_):
            """ Check the change of sign for input signal """
            return in1_ * in2_ < 0

        def sample_zc(self, in_):
            """ sample the input and check the zerocross
                - tick value updated
                - trigger flag rised """
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
            """ Questa funzione verifica la correttezza dello zero cross """
            if self.zc_val < LineIn.MIN_ZC:
                return SysErr().set_alarm(-1, "zerocross under minimum:" + str(self.zc_val))
            # Controllo se zerocross rs oltre il massimo
            elif self.zc_val > LineIn.MAX_ZC:
                return SysErr().set_alarm(-1, "zerocross over maximum: " + str(self.zc_val))
            return 0

    def __init__(self):
        self.zerocross_rs = self.ZeroCross()
        self.zerocross_ts = self.ZeroCross()
        self.zc_RS_TS_cnt = 0
        self.zc_TS_RS_cnt = 0
        self.zc_RS_TS_val = 0
        self.zc_TS_RS_val = 0
        self.zc_RS_trig_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.zc_TS_trig_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.fail_phases_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)


    def reset(self):
        self.zerocross_rs.reset()
        self.zerocross_ts.reset()
        self.zc_RS_TS_cnt = 0
        self.zc_TS_RS_cnt = 0
        self.zc_RS_TS_val = 0
        self.zc_TS_RS_val = 0

    def _check_sequence(self):
        """ Controllo la sequenza delle fasi:
            - Se sono all'interno dell'intervallo buono tutto ok
            - Se sono all'interno dell'intervllo sbagliato allora errore sequenza fasi
            - Else anomalia nelle fasi """
        if self.MIN_CROSS_LIM < self.zc_TS_RS_val < self.MAX_CROSS_LIM:
            return
        elif self.MIN_CROSS_WRONGSEQ < self.zc_TS_RS_val < self.MAX_CROSS_WRONGSEQ:
            # SysErr().set_alarm(-1,"Wrong phases sequence")
            MyReport().rpt_print("Wrong phases sequence")
        else:
            # SysErr().set_alarm(-1,"Error in phases")
            MyReport().rpt_print("Error in phases")

    def sample_and_check(self, in_rs_, in_ts_):
        """ This is the function to sample and check the zerocross of the two singla input
            and verify the cross signals distance """
        self.zerocross_rs.zc_cnt += 1
        self.zerocross_ts.zc_cnt += 1
        self.zc_RS_TS_cnt += 1
        self.zc_TS_RS_cnt += 1

        if self.zerocross_rs.sample_zc(in_rs_):
            self.zc_TS_RS_val = self.zc_TS_RS_cnt
            self.zc_RS_TS_cnt = 0

        if self.zerocross_ts.sample_zc(in_ts_):
            self.zc_RS_TS_val = self.zc_RS_TS_cnt
            self.zc_TS_RS_cnt = 0

        if (self.zerocross_rs.zc_trig >= 0) and (self.zerocross_ts.zc_trig >= 0):
            if (self.zerocross_rs.zc_trig > 0) or (self.zerocross_ts.zc_trig > 0):

                if self.zerocross_rs.zc_trig > 0:
                    self.zerocross_rs.check_zc()
                    self._check_sequence()

                if self.zerocross_ts.zc_trig > 0:
                    self.zerocross_ts.check_zc()

        self.plot_sample()

    def plot_sample(self):
        self.zc_RS_trig_v.append(int(self.zerocross_rs.zc_trig) * CnfAfe().AMPLITUDE)
        self.zc_TS_trig_v.append(int(self.zerocross_ts.zc_trig) * CnfAfe().AMPLITUDE)

    def report_debug(self):
        MyReport().rpt_print("RS: {0} - TS: {0}"
                             .format(str(self.zerocross_rs.zc_val))
                             .format(str(self.zerocross_ts.zc_val)))
        MyReport().rpt_print("TS to RS: {0}".format(str(self.zc_TS_RS_val)))
        MyReport().rpt_print("RS to TS: {0}".format(str(self.zc_RS_TS_val)))


