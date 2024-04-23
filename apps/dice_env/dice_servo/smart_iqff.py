""" In questo modulo il calcolo della companesazione della corrente in base al profilo di coppia delle macchine
    jacquard """
import math

import numpy as np
from matplotlib import pyplot as plt

from my_plotter import MyPlotter
from my_trigo import _sinAq, _cosAq
from range_limits import check_s32
from report import MyReport
from tools import CheckSigned32


class SmartIqff:
    """ Calcolo della componente Iq feed forward con compensazione della coppia """

    F2_FACTOR_REF = 1.8
    F2_FACTOR_VAL = 0.8

    HOOKS_MAX = 100
    HOOKS_MIN = 0
    MAX_LOOM_SPEED = 1200
    MIN_LOOM_SPEED = 450

    THETA_RANGE = 1024
    ACT_THETA_MAX = 1023  # Questo il range reale del theta
    ACT_THETA_MIN = 0  # Questo il range reale del theta
    TRIGO_THETA_RANGE = 2 ** 14 - 1
    _pix2e16 = 205887

    def __init__(self, dice_):
        self.dice = dice_

        self.par_speed_loom_min = 450  # Valori presi da excel
        self.par_speed_loom_max = 1200  # Valori presi da excel

        self.par_ch_max = 2368
        self.par_ch_min = 200

        self.par_foul_max = 200
        self.par_foul_min = 20

        self.par_rend = 0.9
        self.par_amplitude = -2.15  # constant, depends only by machine model

        self.k_rad = None
        self.k_foul = None
        self.k_ch_delta = None
        self.k_speed_loom_delta = None

        self.csj_k1_factor = None
        self.csj_k1_dw = None
        self.csj_k1_up = None

        self.cdj_k_speed = None
        self.cdj_k_speed_quad = None

        self.act_hooks_up = None
        self.act_hooks_dw = None
        self.var_loom_speed_rpm = None

        self.cdj1 = list()
        self.cdj2 = list()
        self.cdj3 = list()

        self.crj_up = list()
        self.crj_dw = list()
        self.crj = list()

        self.c_dyn_j = list()

        self.init()
        self.on_pick()
        self.on_speed()

    def init(self):
        """ Funzione che equivale alla init di dice, con la configurazione del file parametri inizializziamo
            tutto ciò che rimane statico dall'accensione """
        self.k_ch_delta = self.par_ch_max - self.par_ch_min
        self.k_foul = (self.par_foul_max - self.par_foul_min) / (2 * 1000)
        self.k_rad = self.k_ch_delta / self.k_foul
        self.k_speed_loom_delta = (self.MAX_LOOM_SPEED - self.MIN_LOOM_SPEED)

        # Questi possono essere calcolati nella init
        k_foul_8shifted = np.int32(self.k_foul * 2 ** 8)
        self.csj_k1_factor = 10 * k_foul_8shifted

    def on_pick(self):
        """ Calcolo dei fattori che cambiano ad ogni battuta, presumibilmente quando arriva il PDO che gestisce
            i parametri di battuta """
        self.act_hooks_up = 50          # da aggiornare ad ogni battuta
        self.act_hooks_dw = 50          # da aggiornare ad ogni battuta

        # Questi fattori devono essere calcolati ogni battuta
        self.csj_k1_up = self.csj_k1_factor * np.int32(self.act_hooks_up)
        self.csj_k1_dw = self.csj_k1_factor * np.int32(self.act_hooks_dw)

    def on_speed(self):
        """ Questa funzione è quella che calcola la velocità del telaio e i relativi parametri dipendenti. Ancora
            da definire quando chiamarla """
        self.var_loom_speed_rpm = 500  # da calcolare ogni volta e da definire quando

        self.cdj_k_speed = (1.8 - 0.8 * (
                (self.var_loom_speed_rpm - self.MIN_LOOM_SPEED) /
                (self.MAX_LOOM_SPEED - self.MIN_LOOM_SPEED)))

        self.cdj_k_speed_quad = ((self.var_loom_speed_rpm * math.pi / (60 * 2)) ** 2)
    def on_irq(self):
        """ Questa è la funzione che viene chiamate sotto irq e che esegue i calcoli che dipendono dal theta"""

    def get_trigo_range(self):
        return 1 if not self.dice else self.TRIGO_THETA_RANGE

    def get_theta(self, theta_):
        if self.dice:
            return np.int32(theta_ * (self.THETA_RANGE / (2 * math.pi)))
        else:
            return theta_

    def trigo_sin(self, theta_):
        if self.dice:
            return _sinAq(np.int32(theta_))
        else:
            return np.sin(theta_)

    def get_f2_factor_ref(self):
        if self.dice:
            return np.int32(self.F2_FACTOR_REF * 1024)
        else:
            return self.F2_FACTOR_REF

    def get_f2_factor_val(self):
        if self.dice:
            return np.int32(self.F2_FACTOR_VAL * 1024)
        else:
            return self.F2_FACTOR_VAL

    def mul_amplitude(self, val_):
        if self.dice:
            #it (6)	 mul (137)	 sh (6)	 err% (0.43604651162790287)
            v = float(val_) * 137
            if not CheckSigned32(v):
                MyReport().rpt_print("error overflow")
            return -(np.int32(v) >> 6)
        else:
            return val_ * self.par_amplitude

    def trigo_cos(self, theta_):
        if self.dice:
            return _cosAq(np.int32(theta_))
        else:
            return np.cos(theta_)

    def set_s32(self, v_):
        if not CheckSigned32(v_):
            MyReport().rpt_error(-2, "Overflow")
        return np.int32(v_)


    def cdj_calc_theo(self,theta_):
        # Calcolo della coppia dinamica teroica
        self.c_dyn_j = -(self.cdj_k_speed * self.par_amplitude *
                        self.cdj_k_speed_quad * np.sin(2 * theta_))

    

    def cdj_calc(self, theta_):
        trigo_range = self.get_trigo_range()
        theta_ = self.get_theta(theta_)
        if not self.dice:
            self.cdj_calc_theo(theta_)
        else:
            self.c_dyn_j = list()
            # Calcolo del fattore f1 che è una costante
            # (math.pi * math.pi) / (120 * 120)
            # in dice abbiamo _pix2e16 che è math*pi * 65536 quindi facciamo:
            # f1 = (_pix2e16/120) * (_pix2e16/120)
            # Calcolo il fattore costante tenendo attivo uno shift di 16 che compensero' in un secondo
            # momento
            cd_k1_32shifted = (self._pix2e16 ** 2) / ((2 * 60) ** 2)
            MyReport().rpt_print("k1_32shifted = " + str(cd_k1_32shifted) + "\n")

            ktot_32shifted = cd_k1_32shifted * self.par_amplitude
            MyReport().rpt_print("ktot_32shifted = " + str(ktot_32shifted) + "\n")

            #for ampl in np.linspace(0.02, 20, 20):
            #    kk = k1_32shifted * ampl
            #    MyReport().rpt_print("ktot_32shifted [" + str(ampl) + "] = " + str(kk))

            # Calcolo del fattore F2 della formnula, siccome è un valore piccolo teniamo un moltiplicatore
            # 1024
            f2_ref_10shifted = self.get_f2_factor_ref()  # Calcolo il reference 1,8 moltiplicandolo per 1024
            MyReport().rpt_print("f2_ref_10shifted = " + str(f2_ref_10shifted))
            f2_val_10shifted = self.get_f2_factor_val()  # Calcolo il valore 0,8 moltiplicandolo per 1024
            MyReport().rpt_print("f2_val_10shifted = " + str(f2_val_10shifted))
            f2_speed_div = np.int32(self.k_speed_loom_delta)
            MyReport().rpt_print("f2_speed_div = " + str(f2_speed_div))

            for speed in np.linspace(450, 1200, 20):
                f2_speed_num = np.int32(speed - self.MIN_LOOM_SPEED)
                # Questo è il fattore F2 della formula ma calcolato con un fattore di shift 10 per mantenere
                # la risoluzione
                f2_10shifted = np.int32(f2_ref_10shifted - (f2_val_10shifted * f2_speed_num / f2_speed_div))
                MyReport().rpt_print("f2_10shifted [" + str(speed) + "] = " + str(f2_10shifted))

            for th in theta_:
                # calcolo della coppia dinamica nel caso dice
                # cdj = -((LoomSpeed/2)*(pi/60))**2 * Amplitude * F2 * sin(2*Theta)
                # cdj = - Ls^2 * k1 * A * f2 * sin(2*theta)
                # cdj = - ( Ls^2 * (k1 * A) * f2 * sin(2*theta)  )

                f2_speed_num = np.int32(self.var_loom_speed_rpm - self.MIN_LOOM_SPEED)
                # Questo è il fattore F2 della formula ma calcolato con un fattore di shift 10 per mantenere
                # la risoluzione
                f2_10shifted = np.int32(f2_ref_10shifted - (f2_val_10shifted * f2_speed_num / f2_speed_div))

                # Prima di tutto calcolo il sin(2*Theta) usando le funzioni trigonometriche uscendo con un valore
                # compreso tra -2**14 e 2**14
                cdj1_ = np.int32(self.trigo_sin(2 * th))

                # cdj = sin(2* theta) * f2_1024
                cdj2_ = np.int32(cdj1_ * f2_10shifted)

                # A questo punto posso moltiplicare per Amplitude e dividere per 1024 visto che il valore tornato dal
                # sin è un valore alto. La dvisione è in 2 fasi per evitare overflow
                cdj3_ = np.int32(self.mul_amplitude(cdj2_ >> 5)) >> 5  # moltiplico per Amplitude e divido per 1024

                # Ora aggiungo il fattore quadratico

                cdj4_ = np.int32(cdj3_ * (self.var_loom_speed_rpm * math.pi) ** 2 / 120 ** 2)  # quadratic effort

                # Questo lo shift dovuto al fatto che esco dalla trigo con 2*14 invece che con 1
                cdj4_ = cdj4_ >> 14
                # Applico il segno meno della formula
                cdj4_ = -cdj4_

                #cdj1.append(cdj1_)
                #cdj2.append(cdj2_)
                #cdj3.append(cdj3_)
                #cdj.append(cdj4_)
                self.c_dyn_j.append(cdj4_)

        input_cdj = MyPlotter(plt, 100)
        """pos_fig = 511
        input_cdj.add_subplot(pos_fig, "Cdj" + str(self.dice), "theta")
        input_cdj.set_subplot_range(pos_fig, np.min(theta_), np.max(theta_))
        input_cdj.add_samples(pos_fig, theta_)
        pos_fig = 512
        input_cdj.add_subplot(pos_fig, "Cdj" + str(self.dice), "Cdj1", )
        input_cdj.set_subplot_range(pos_fig, np.min(cdj1), np.max(cdj1))
        input_cdj.add_samples(pos_fig, cdj1)
        pos_fig = 513
        input_cdj.add_subplot(pos_fig, "Cdj" + str(self.dice), "Cdj2", )
        input_cdj.set_subplot_range(pos_fig, np.min(cdj2), np.max(cdj2))
        input_cdj.add_samples(pos_fig, cdj2)
        pos_fig = 514
        input_cdj.add_subplot(pos_fig, "Cdj" + str(self.dice), "Cdj3", )
        input_cdj.set_subplot_range(pos_fig, np.min(cdj3), np.max(cdj3))
        input_cdj.add_samples(pos_fig, cdj3)"""
        pos_fig = 515
        input_cdj.add_subplot(pos_fig, "Cdj" + str(self.dice), "self.c_dyn_j", )
        input_cdj.set_subplot_range(pos_fig, np.min(self.c_dyn_j), np.max(self.c_dyn_j))
        input_cdj.add_samples(pos_fig, self.c_dyn_j)

    def csj_calc(self, theta_):
        trigo_range = self.get_trigo_range()
        theta_ = self.get_theta(theta_)
        crj_up = list()
        crj_dw = list()
        crj = list()
        csf = list()
        csj = list()

        if not self.dice:
            # Calcolo della coppia statica
            crj_up_ori = (((self.par_ch_max * self.act_hooks_up) -
                           (self.k_rad * self.act_hooks_up * self.k_foul * (1 - np.sin(theta_)) / 2)) *
                          10 * self.k_foul * np.cos(theta_) / 2)

            crj_dw_ori = (((self.par_ch_max * self.act_hooks_dw) -
                           (self.k_rad * self.act_hooks_dw * self.k_foul * (1 - np.sin(theta_ + math.pi)) / 2)) *
                          10 * self.k_foul * np.cos(theta_ + math.pi) / 2)

            # dato che cos(pi + theta) = -cos(theta) e sin(pi + theta) = -sin(theta)
            crj_up = self.act_hooks_up
            crj_up *= (trigo_range * self.par_ch_max) - (self.k_ch_delta * (trigo_range - self.trigo_sin(theta_)) / 2)
            crj_up *= (10 * self.k_foul * np.cos(theta_) / 2)

            crj_dw = -self.act_hooks_dw
            crj_dw *= (trigo_range * self.par_ch_max) - (self.k_ch_delta * (trigo_range - (-self.trigo_sin(theta_))) / 2)
            crj_dw *= (10 * self.k_foul * (-np.cos(theta_)) / 2)

            crj = crj_up_ori + crj_dw_ori
            csf = abs(crj) * (1 - self.par_rend)
            csj = crj + csf

        else:
            self.par_ch_max = np.int32(self.par_ch_max)
            self.k_ch_delta = np.int32(self.k_ch_delta)

            for th in theta_:
                crj_up_ = 1
                crj_up_ = self.set_s32(crj_up_ * (
                            (trigo_range * self.par_ch_max) - (self.k_ch_delta * (trigo_range - self.trigo_sin(th)) / 2)))
                crj_up_ >>= 9
                crj_up_ = self.set_s32(crj_up_ * self.csj_k1_up)
                crj_up_ >>= 6
                crj_up_ >>= 7

                crj_up_ = self.set_s32(crj_up_ * self.trigo_cos(th) / 2)
                crj_up_ >>= 7
                crj_up_ >>= 7

                # Calcolo della componente down
                crj_dw_ = 1
                crj_dw_ = self.set_s32(crj_dw_ * ((trigo_range * self.par_ch_max) - (
                            self.k_ch_delta * (trigo_range - (-self.trigo_sin(th))) / 2)))
                crj_dw_ >>= 9
                crj_dw_ = self.set_s32(crj_dw_ * self.csj_k1_dw)
                crj_dw_ >>= 6
                crj_dw_ >>= 7

                crj_dw_ = self.set_s32(crj_dw_ * (-self.trigo_cos(th)) / 2)
                crj_dw_ >>= 7
                crj_dw_ >>= 7

                crj_ = crj_up_ + crj_dw_
                csf_ = abs(crj_) * (1 - self.par_rend)

                # Infine calcolo la coppia statica
                csj_ = crj_ + csf_

                # butto tutto nei vettori per il plot
                crj_up.append(crj_up_)
                crj_dw.append(crj_dw_)
                crj.append(crj_)
                csf.append(csf_)
                csj.append(csj_)

        input_csj = MyPlotter(plt, 100)
        pos_fig = 511
        input_csj.add_subplot(pos_fig, "Csj: dice=" + str(self.dice), "theta")
        input_csj.set_subplot_range(pos_fig, np.min(theta_), np.max(theta_))
        input_csj.add_samples(pos_fig, theta_)
        pos_fig = 512
        input_csj.add_subplot(pos_fig, "Csj: dice=" + str(self.dice), "Crj_up")
        input_csj.set_subplot_range(pos_fig, np.min(crj_up), np.max(crj_up))
        input_csj.add_samples(pos_fig, crj_up)
        pos_fig = 513
        input_csj.add_subplot(pos_fig, "Csj: dice=" + str(self.dice), "Crj_dw")
        input_csj.set_subplot_range(pos_fig, np.min(crj_dw), np.max(crj_dw))
        input_csj.add_samples(pos_fig, crj_dw)
        pos_fig = 514
        input_csj.add_subplot(pos_fig, "Csj: dice=" + str(self.dice), "Crj")
        input_csj.set_subplot_range(pos_fig, np.min(crj), np.max(crj))
        input_csj.add_samples(pos_fig, crj)
        pos_fig = 515
        input_csj.add_subplot(pos_fig, "Csj: dice=" + str(self.dice), "Csj")
        input_csj.set_subplot_range(pos_fig, np.min(csj), np.max(csj))
        input_csj.add_samples(pos_fig, csj)

        return csj

    def calculate(self):
        theta_test = np.linspace(0, np.pi * 2, 100)
        self.csj_calc(theta_test)
        self.cdj_calc(theta_test)
        self.dice = True
        self.csj_calc(theta_test)
        self.cdj_calc(theta_test)
        plt.show()


report = MyReport("../../", "iqff_report.txt")
sm = SmartIqff(False)
sm.calculate()
