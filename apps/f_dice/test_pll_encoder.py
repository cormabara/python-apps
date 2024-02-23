"""
Questo modulo testa il PLL che dovrebbe agganciare l'encoder
L'ingresso è la posizione assoluta prendendo come riferimento di zero un punto
arbitrario (non importa quale)
Passando dal PID otteniamo una SPEED che poi integriamo per ottenere la posizione
"""
import math
import random

import numpy as np

from my_pid import XIntegral
from report import rpt_open, rpt_print
from tools import SinForm, Ramp
from my_types import U32_MAX, S32_MAX
from apps.f_dice.modules.pll_encoder import PllEncoder
from tools import MyPlot

REAL_MODE = False

DEEP_SEC = 0.1  # time deep of simulation
PLL_SAMPLE_TIME = 200E-6  # Sample time for the PLL
PLL_SAMPLE_FRQUENCY_HZ = 1/PLL_SAMPLE_TIME
PLL_NUMSAMPLES = int((DEEP_SEC / PLL_SAMPLE_TIME) + 1)

ELESHAFT_SAMPLE_TIME = 1E-3  # Sample time of the electric shaft module
ELESHAFT_NUMSAMPLES = int((DEEP_SEC / ELESHAFT_SAMPLE_TIME) + 1)  # eleshaft samples

ENCODER_REFSPEED_RPM = 100  # Velocità di riferimento in rpm
OMEGA_NOISE_RPM = 12000  # frequenza del rumore sinusoidale in rpm
QEP_RESOLUTION = 40960
MAXSPEED= 2**31                  # Limit for the speed (antiwindup)
MAXERRI = S32_MAX        # Limit for the integral error

real_pos = 0


def rpm_2_radsec(rpm_):
    return (rpm_ / 60) * 2 * math.pi

def radsec_2_qepsec(radsec_):
    return (radsec_ * QEP_RESOLUTION) / (2 * math.pi)

def radsec_2_qeptick(radsec_):
    return radsec_2_qepsec(radsec_)/5000

def qeptick_2_rps256(qeptick_):
    return qeptick_ * (5000*256/QEP_RESOLUTION)

def rps256_2_qeptick(rps256_):
    return rps256_ / (5000*256/QEP_RESOLUTION)


def rad_2_qep(rad_):
    return ((rad_ * QEP_RESOLUTION) / (2 * math.pi)) % QEP_RESOLUTION


def noise_speed_rs(time_):
    return (rpm_2_radsec(ENCODER_REFSPEED_RPM) * 20 / 100) * math.sin(rpm_2_radsec(OMEGA_NOISE_RPM) * time_)


def QepSimulation(deep_, pre_perc,rise_perc, fall_perc, post_perc):
    """ Questa funzione simula la QEP, partendo da un profilo di velocità arbitrario crea i campioni di
    posizione che uscirebbero dalla qep
    Ritorna una matrice per colonne con:
    col0: array dei tempi
    col1: array della input speed rad/sec
    col2: array della posizione in radianti """

    # Calcolo il vettore dei tempi per la profondita' richiesta
    time_samples = [ind * PLL_SAMPLE_TIME for ind in range(0, deep_)]

    # Calcolo la velocità reale come la velocità di riferimento + una componente sinusoidale del 10%
    # ref_speed_rs = rpm2radsec(ENCODER_REFSPEED_RPM)
    pre_deep  = int(deep_ * pre_perc / 100)
    rise_deep = int(deep_ * rise_perc / 100)
    fall_deep = int(deep_ * fall_perc / 100)
    post_deep = int(deep_ * post_perc / 100)
    flat_deep = deep_ - pre_deep - rise_deep - fall_deep - post_deep

    pre_speed_rs  = [0 for ind in range(0,pre_deep)]
    rise_speed_rs = Ramp(0, 1000, rise_deep)
    fall_speed_rs = Ramp(1000, 0, fall_deep)
    post_speed_rs  = [0 for ind in range(0,post_deep)]
    flat_speed_rs = [1000 for ind in range(0,flat_deep)]

    moving_deep = rise_deep + flat_deep + fall_deep
    ref_speed_rs = rise_speed_rs + flat_speed_rs + fall_speed_rs

    # qui devo aggiungere il disturbo
    ref_speed_rs = [ref_speed_rs[ind] + noise_speed_rs(time_samples[ind]) for ind in range(0, moving_deep)]

    # quindi aggiungo le parti pre e post
    ref_speed_rs = pre_speed_rs + ref_speed_rs + post_speed_rs
    ref_speed_qept = radsec_2_qeptick(np.array(ref_speed_rs))

    # ora calcolo il valore della qep a distanza di 200uS considrando il profilo di valocità
    # qep = [speed_radsec[ind] * PLL_SAMPLE_TIME for ind in range(0, deep_)]
    pos_int = XIntegral(False)
    qep = [(pos_int.increment(ref_speed_qept[ind], 0, U32_MAX) % QEP_RESOLUTION) for ind in
           range(0, deep_)]

    retval = np.vstack([time_samples, ref_speed_qept, qep])
    return retval


rpt_open("../../reports", "pll_encoder_test.txt")
in_matrix = QepSimulation(PLL_NUMSAMPLES, 10, 25, 25, 10)
time_in_v = in_matrix[0, :]  # time vector (x axis)
speed_in_v_qeptick = in_matrix[1, :]  # speed vector input in rad/sec
pos_in_v_qep = in_matrix[2, :]  # position vector input qep unity

pllEncoder = PllEncoder(REAL_MODE, QEP_RESOLUTION, PLL_SAMPLE_FRQUENCY_HZ, False)
pllEncoder.setProportional(140, 7)
pllEncoder.setIntegral(200, 9)
pllEncoder.setDerivative(0, 0)
pllEncoder.setLimits(-MAXSPEED, MAXSPEED, MAXERRI)

effort_v = []
pos_out_v = []
speed_out_v_qeptick = []
pos_err1_v = []
pos_err2_v = []

for sample in range(0, PLL_NUMSAMPLES):
    pllEncoder.calculate(pos_in_v_qep[int(sample)],speed_in_v_qeptick[int(sample)])
    pos_out_v.append(pllEncoder.obsPos)
    pos_err1_v.append(pllEncoder.errPos1)
    pos_err2_v.append(pllEncoder.errPos2)
    effort_v.append(pllEncoder.effort)
    speed_out_v_qeptick.append(pllEncoder.obsSpeed)

plt = MyPlot(3, 1, 1, "Speed", time_in_v, speed_in_v_qeptick, speed_out_v_qeptick)
MyPlot(3, 1, 2, "Pos", time_in_v, pos_in_v_qep, pos_out_v)
MyPlot(3, 1, 3, "Internal", time_in_v, pos_err1_v, pos_err2_v)

rpt_print("max error pos: " + str(np.max(pos_err2_v)))
rpt_print("max error neg: " + str(np.min(pos_err2_v)))
rpt_print("mean error: " + str(np.mean(pos_err2_v)))
plt.show()
