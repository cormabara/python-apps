import math

import sys
import numpy
import numpy as np
from my_types import S32
from numpy import int32

from range_limits import saturate_out_of_range
from tools import div_sqr3, divshx

# shift for the look up table value. That means the available values are from 0 to 1023
TRIGO_SHIFT = 14

SIMTABDIM_POW = 8
SIMTABDIM = (1 << SIMTABDIM_POW)
SIMTABDIM_HIHI = (1 << (SIMTABDIM_POW + 1))  # Valore per determinare half bassa / alta
SIMTABDIM_HI = (1 << SIMTABDIM_POW)  # Valore per determinare tra quarto basso e alto
TRIGO_THETA_RANGE = SIMTABDIM * 4  # Range of the input theta


# Funzione per la generazione della tabella seno coseno
def _getSinTable(deep_):
    """Create the lookup-table to get the sin from theta value"""
    step = (math.pi / 2) / deep_
    in_s = numpy.arange(0, (math.pi / 2) + step, step)
    in_v = np.round((2 ** TRIGO_SHIFT) * np.sin(in_s), 0)
    return in_v


# Funzione per la generazione della tabella seno coseno
def _getCosTable(deep_):
    """Create the lookup-table to get the sin from theta value"""
    step = (math.pi / 2) / deep_
    in_s = numpy.arange(0, (math.pi / 2) + step, step)
    in_v = np.round((2 ** TRIGO_SHIFT) * np.cos(in_s), 0)
    return in_v


# tabella del seno ha valori (0..1), ma per esigenze di calcolo e' codificata a 14[b] nel range [0..16383]
# Questa è la tabella originale presente in DICE
TabSin_old = [
    0,
    101,
    201,
    302,
    402,
    503,
    603,
    703,
    804,
    904,
    1005,
    1105,
    1205,
    1305,
    1406,
    1506,
    1606,
    1706,
    1806,
    1906,
    2005,
    2105,
    2205,
    2304,
    2404,
    2503,
    2603,
    2702,
    2801,
    2900,
    2999,
    3098,
    3196,
    3295,
    3393,
    3491,
    3590,
    3688,
    3785,
    3883,
    3981,
    4078,
    4175,
    4273,
    4370,
    4466,
    4563,
    4659,
    4756,
    4852,
    4948,
    5044,
    5139,
    5234,
    5330,
    5425,
    5519,
    5614,
    5708,
    5802,
    5896,
    5990,
    6083,
    6177,
    6270,
    6362,
    6455,
    6547,
    6639,
    6731,
    6822,
    6914,
    7005,
    7095,
    7186,
    7276,
    7366,
    7456,
    7545,
    7634,
    7723,
    7811,
    7900,
    7988,
    8075,
    8162,
    8249,
    8336,
    8423,
    8509,
    8594,
    8680,
    8765,
    8850,
    8934,
    9018,
    9102,
    9185,
    9268,
    9351,
    9433,
    9515,
    9597,
    9678,
    9759,
    9840,
    9920,
    10000,
    10079,
    10158,
    10237,
    10315,
    10393,
    10471,
    10548,
    10625,
    10701,
    10777,
    10852,
    10927,
    11002,
    11076,
    11150,
    11224,
    11297,
    11369,
    11441,
    11513,
    11585,
    11655,
    11726,
    11796,
    11865,
    11934,
    12003,
    12071,
    12139,
    12206,
    12273,
    12339,
    12405,
    12471,
    12536,
    12600,
    12664,
    12728,
    12791,
    12853,
    12915,
    12977,
    13038,
    13099,
    13159,
    13219,
    13278,
    13336,
    13394,
    13452,
    13509,
    13566,
    13622,
    13678,
    13733,
    13787,
    13841,
    13895,
    13948,
    14000,
    14052,
    14104,
    14154,
    14205,
    14255,
    14304,
    14353,
    14401,
    14449,
    14496,
    14542,
    14588,
    14634,
    14679,
    14723,
    14767,
    14810,
    14853,
    14895,
    14936,
    14977,
    15018,
    15058,
    15097,
    15136,
    15174,
    15212,
    15249,
    15285,
    15321,
    15356,
    15391,
    15425,
    15459,
    15492,
    15524,
    15556,
    15587,
    15618,
    15648,
    15678,
    15706,
    15735,
    15762,
    15790,
    15816,
    15842,
    15867,
    15892,
    15916,
    15940,
    15963,
    15985,
    16007,
    16028,
    16048,
    16068,
    16088,
    16106,
    16124,
    16142,
    16159,
    16175,
    16191,
    16206,
    16220,
    16234,
    16247,
    16260,
    16272,
    16283,
    16294,
    16304,
    16314,
    16323,
    16331,
    16339,
    16346,
    16352,
    16358,
    16363,
    16368,
    16372,
    16375,
    16378,
    16380,
    16382,
    16383,
]

TabSin = _getSinTable(SIMTABDIM)
TabCos = _getCosTable(SIMTABDIM)


# Macro per determinare in quale settore si trova l'angolo passato
# 0 - 90° primo settore
# 90° - 180° secondo settore
# 180° - 270° terzo settore
# 270° - 359° quarto settore
# ricordando che l'angolo è espresso in un range di TRIGO_THETA_RANGE
def _tabSector(index_):
    if not (index_ & SIMTABDIM_HIHI):
        if not (index_ & SIMTABDIM_HI):
            return 1
        else:
            return 2
    else:
        if not (index_ & SIMTABDIM_HI):
            return 3
        else:
            return 4


# operazioni per quadrante base, "teta_" qualunque, viene riportato (0..255 ==> 0°..< 90°)
def _sin_q(teta_):
    return TabSin[(teta_ & (SIMTABDIM - 1))]


# ATTENZIONE: siccome il coseno percorre la tabella in ordine decrescente<
def _cos_q(teta_):
    return TabSin[SIMTABDIM - (teta_ & (SIMTABDIM - 1))]


# ...operazioni per ogni singolo quadrante...
def _sin1q(theta_): return _sin_q(theta_)


def _cos1q(theta_): return _cos_q(theta_)


def _sin2q(theta_): return _cos_q(theta_)


def _cos2q(theta_): return -_sin_q(theta_)


def _sin3q(theta_):        return -_sin_q(theta_)


def _cos3q(theta_):        return -_cos_q(theta_)


def _sin4q(theta_):        return -_cos_q(theta_)


def _cos4q(theta_):        return _sin_q(theta_)


# ...e generiche, per qualunque valore di "teta_"
def _sinAq(theta_: int):
    # "teta_" puo' avere un valore qualsiasi, positivo o negativo;
    # ricordando la proporzione (0°..360° ==> 0..1024) e le proprieta' dei numeri binari...
    theta_ = np.round(theta_)
    sector = _tabSector(theta_)
    if sector == 1:
        return _sin1q(theta_)  # (0° <= teta < 90°)
    elif sector == 2:
        return _sin2q(theta_)  # (90° <= teta < 180°)
    elif sector == 3:
        return _sin3q(theta_)  # (180° <= teta < 270°)
    else:
        return _sin4q(theta_)  # (270° <= teta < 360°)


def _cosAq(theta_):
    theta_ = round(theta_)
    sector = _tabSector(theta_)
    if sector == 1:
        return _cos1q(theta_)  # (0° <= teta < 90°)
    elif sector == 2:
        return _cos2q(theta_)  # (90° <= teta < 180°)
    elif sector == 3:
        return _cos3q(theta_)  # (180° <= teta < 270°)
    else:
        return _cos4q(theta_)  # (270° <= teta < 360°)


def _TrigoCombLow(A_, B_, teta_):
    val = (A_ * _sinAq(teta_)) + (B_ * _cosAq(teta_))
    # return divshx(val, TRIGO_SHIFT);
    return val


def _TrigoComb(A_, B_, teta_, min_, max_):
    return saturate_out_of_range(_TrigoCombLow(A_, B_, teta_), min_, max_)


def trigo_dir_clarke(real_, u_, v_, w_, min_, max_):
    # Clarke diretta
    if real_:
        u_ = S32(u_)
        v_ = S32(v_)
        alpha = S32(u_)
        beta = S32(div_sqr3(u_ + 2 * v_))
        beta = S32(saturate_out_of_range(beta, min_, max_))
    else:
        inm = np.array([u_, v_, w_])
        dctm = np.array([[1, -1 / 2, -1 / 2], [0, math.sqrt(3) / 2, -math.sqrt(3) / 2], [1 / 2, 1 / 2, 1 / 2]])
        out = (2 / 3) * numpy.matmul(dctm, inm)
        alpha = out[0]
        beta = out[1]

    return np.array([alpha, beta])

def trigo_rev_clarke(real_, alpha_, beta_):
    """ Clarke reverse from alpha beta to v1,v2,v3 """
    if real_:
        v1 = 0
        v2 = 0
        v3 = 0
        return np.array([v1, v2,v3])
    else:
        inm = np.array([alpha_, beta_, 0])
        dctm = np.array([[1, 0, 1], [-(1/2), (math.sqrt(3) / 2), 1], [-(1 / 2), -(math.sqrt(3) / 2), 1]])
        out = (2 / 3) * numpy.matmul(dctm, inm)
        v1 = out[0]
        v2 = out[1]
        v3 = out[2]
        return np.array([v1, v2, v3])


def trigo_dir_clarke_v(u_, v_, w_):
    # Clarke diretta con vettori in ingresso
    alpha = np.zeros(len(u_))
    beta = np.zeros(len(u_))
    for ind in range(0, len(u_)):
        inm = np.array([u_[ind], v_[ind], w_[ind]])
        dctm = np.array([[1, -1 / 2, -1 / 2], [0, math.sqrt(3) / 2, -math.sqrt(3) / 2], [1 / 2, 1 / 2, 1 / 2]])
        out = (2 / 3) * numpy.matmul(dctm, inm)
        alpha[ind] = out[0]
        beta[ind] = out[1]

    return np.array([alpha, beta])


def trigo_dir_park(real_, alpha_, beta_, theta_, min_, max_):
    # La dirpark reale accetta un valore del theta che è in
    # un range di 0-1024 mentre quella teorica in radianti
    if real_:
        theta_ = round(theta_)
        d = S32(_TrigoComb(beta_, alpha_, theta_, min_, max_))
        q = S32(_TrigoComb(-alpha_, beta_, theta_, min_, max_))
    else:
        d = alpha_ * math.cos(theta_) + beta_ * math.sin(theta_)
        q = -alpha_ * math.sin(theta_) + beta_ * math.cos(theta_)

    return np.array([d, q])


def trigo_rev_park(real_, vald_, valq_, theta_, min_, max_):
    """ Reverse park from d,q to alpha, beta """
    if real_:
        valpha = _TrigoComb(-valq_, vald_, theta_, min_, max_)
        vbeta = _TrigoComb(vald_, valq_, theta_, min_, max_)
    else:
        valpha = - valq_ * math.sin(theta_) + vald_ * math.cos(theta_)
        vbeta = vald_ * math.sin(theta_) + valq_ * math.cos(theta_)

    return np.array([valpha, vbeta])


def sinAq(theta_):
    return _sinAq(theta_)


def cosAq(theta_):
    return _cosAq(theta_)
