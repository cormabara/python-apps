import math
import string
import sys
from enum import IntEnum

import numpy
import numpy as np
import pandas
from matplotlib import pyplot as plt

from f_dice.lib.report import MyReport
from f_dice.lib.types import S32_MIN, S32_MAX
from f_dice.lib.my_trigo import TRIGO_SHIFT, TRIGO_THETA_RANGE, DirClarke, DirPark, sinAq, TabSin, TabCos, SIMTABDIM, \
    cosAq
from f_dice.lib.tools import shift_dx, MyPlot

report = MyReport("../../reports", "test_trigo.txt")


def runTest():
    SAMPLES = 1000
    amplitude = 2 ** TRIGO_SHIFT
    step = 2 * math.pi / SAMPLES
    in_v = numpy.arange(0, 2 * math.pi, step)

    alpha_t = numpy.zeros(SAMPLES)
    beta_t = numpy.zeros(SAMPLES)
    ed_t = numpy.zeros(SAMPLES)
    eq_t = numpy.zeros(SAMPLES)
    alpha_r = numpy.zeros(SAMPLES)
    beta_r = numpy.zeros(SAMPLES)
    ed_r = numpy.zeros(SAMPLES)
    eq_r = numpy.zeros(SAMPLES)
    sin_aq = numpy.zeros(SAMPLES)

    theta_t = in_v
    sin_in = numpy.sin(theta_t)
    sin_in = sin_in * amplitude
    theta_r = in_v * (TRIGO_THETA_RANGE / (2 * math.pi))
    u = amplitude * numpy.cos(in_v)
    v = amplitude * numpy.cos(in_v - (2 * math.pi / 3))
    w = amplitude * numpy.cos(in_v - (4 * math.pi / 3))

    for sample in range(SAMPLES):
        alpha_beta_t = DirClarke(False, u[sample], v[sample], w[sample], S32_MIN, S32_MAX)
        alpha_t[sample] = alpha_beta_t[0]
        beta_t[sample] = alpha_beta_t[1]
        ed_eq = DirPark(False, alpha_t[sample], beta_t[sample], theta_t[sample], S32_MIN, S32_MAX)
        ed_t[sample] = ed_eq[0]
        eq_t[sample] = ed_eq[1]

        sin_aq[sample] = sinAq(theta_r[sample])

        alpha_beta = DirClarke(True, u[sample], v[sample], w[sample], S32_MIN, S32_MAX)
        alpha_r[sample] = alpha_beta[0]
        beta_r[sample] = alpha_beta[1]
        ed_eq_r = DirPark(True, alpha_r[sample], beta_r[sample], theta_r[sample], S32_MIN, S32_MAX)
        ed_r[sample] = shift_dx(int(ed_eq_r[0]), TRIGO_SHIFT)
        eq_r[sample] = shift_dx(int(ed_eq_r[1]), TRIGO_SHIFT)
    index = 0

    # Grafico alfa beta
    index += 1
    MyPlot(3, 3, index, "U-V-W", in_v, u, v, w)

    index += 1
    MyPlot(4, 3, 2, "Alpha", in_v, alpha_t, alpha_r)
    MyPlot(4, 3, 3, "Beta", in_v, beta_t, beta_r)

    error_alpha = (alpha_t - alpha_r) * 100 / max(alpha_t);
    error_beta = (beta_t - beta_r) * 100 / max(beta_t);
    MyPlot(4, 3, 4, "Alpha - Beta error", in_v, error_alpha, error_beta)

    MyPlot(4, 3, 5, "Ed", in_v, ed_t, ed_r)
    MyPlot(4, 3, 6, "Eq", in_v, eq_t, eq_r)

    error_ed = (ed_t - ed_r)
    MyPlot(4, 3, 7, "Ed error", in_v, error_ed)
    error_eq = (eq_t - eq_r)
    MyPlot(4, 3, 8, "Eq error", in_v, error_eq)

    MyPlot(4, 3, 9, "sin - sin", in_v, sin_in, sin_aq)
    MyPlot(4, 3, 10, "sin error", in_v, sin_in - sin_aq)

    plt.show()

    meanerr = numpy.mean(sin_in - sin_aq) * 100 / amplitude
    report.rpt_print(str(meanerr))
    maxerr = numpy.max(sin_in - sin_aq) * 100 / amplitude
    report.rpt_print(str(maxerr))


# Funzione per la generazione della tabella seno coseno
def SinTable(deep_, amplitude_):
    """Create the lookup-table to get the sin from theta value"""
    step = (math.pi / 2) / deep_
    in_s = numpy.arange(0, (math.pi / 2), step)
    in_v = np.round(amplitude_ * np.sin(in_s), 0)
    return in_v


# Funzione per la generazione della tabella seno coseno
def CosTable(deep_, amplitude_):
    """Create the lookup-table to get the sin from theta value"""
    step = (math.pi / 2) / deep_
    in_s = numpy.arange(0, (math.pi / 2), step)
    in_v = np.round(amplitude_ * np.cos(in_s), 0)
    return in_v


def sinCosTest(deep_, amplitude_):
    """
    This function calculate the sin and cos in table and theorical form and check the error for the
    sin and cos looking at a quarter of the available range 2*math.pi/4
    :param amplitude_: amplitude of the sin input (number of bit of the ad conversion)
    """
    sin_table = SinTable(deep_, amplitude_)
    cos_table = CosTable(deep_, amplitude_)
    step = (math.pi / 2) / deep_
    in_s = numpy.arange(0, (math.pi / 2), step)
    sin_theo = amplitude_ * np.sin(in_s)
    cos_theo = amplitude_ * np.cos(in_s)
    numpy.set_printoptions(threshold=sys.maxsize)
    report.rpt_sep()

    report.rpt_sep()
    report.rpt_print("## Trigo Sin table")
    report.rpt_print("Sin len: " + str(len(TabSin)))
    report.rpt_print("Sin : " + str(TabSin))

    report.rpt_sep()
    report.rpt_print("## Sin table")
    report.rpt_print("Sin len: " + str(len(sin_table)))
    report.rpt_print("Sin : " + str(sin_table))
    report.rpt_sep()
    report.rpt_print("## Sin Theo")
    report.rpt_print("Sin Theo len: " + str(len(sin_theo)))
    report.rpt_print("Sin Theo : " + str(sin_theo))

    report.rpt_sep()
    report.rpt_print("## Cos table")
    report.rpt_print("Cos len: " + str(len(cos_table)))
    report.rpt_print("Cos : " + str(cos_table))
    report.rpt_print("## Cos Theo")
    report.rpt_print("Cos Theo len: " + str(len(cos_theo)))
    report.rpt_print("Cos Theo : " + str(cos_theo))

    sin_error = sin_theo - sin_table
    cos_error = cos_theo - cos_table
    sin_error_perc = (sin_error / sin_theo) * 100
    cos_error_perc = (cos_error / cos_theo) * 100
    report.rpt_sep()
    report.rpt_print("Sin error : " + str(sin_error))
    report.rpt_print("Sin error % : " + str(sin_error_perc))
    report.rpt_print("Cos error : " + str(cos_error))
    report.rpt_print("Cos error % : " + str(cos_error_perc))

    plot = MyPlot(1, 1, 1, "Sin Error", in_s, sin_error_perc, cos_error_perc)
    plot.show()


def fromCsv(filename_):
    report.rpt_print("\nCALCULATE FROM FILE: " + filename_)
    index = np.transpose(pandas.read_csv(filename_, usecols=[0], header=12).to_numpy())
    data_sin = np.transpose(pandas.read_csv(filename_, usecols=[1], header=12).to_numpy())
    data_cos = np.transpose(pandas.read_csv(filename_, usecols=[2], header=12).to_numpy())
    matrix = np.vstack([index, data_sin, data_cos])
    return matrix


class Columns(IntEnum):
    THETA = 0
    OSC_SIN = 1
    OSC_COS = 2
    THEO_SIN = 3
    THEO_COS = 4
    TAB_SIN = 5
    TAB_COS = 6


def sinCosTestCsv(filename_: string):
    mymatrix = fromCsv(filename_)
    amplitude = max(mymatrix[1])
    index_v = np.zeros(len(mymatrix[0]))
    sin_table = np.zeros(len(mymatrix[0]))
    cos_table = np.zeros(len(mymatrix[0]))
    sin_theo = np.zeros(len(mymatrix[0]))
    cos_theo = np.zeros(len(mymatrix[0]))

    index = 0
    for ii in range(0, len(mymatrix[Columns.THETA])):
        index_v[index] = index
        teta = mymatrix[Columns.THETA][ii]
        sin_table[index] = sinAq(teta)
        cos_table[index] = cosAq(teta)
        theo_value = ((teta % TRIGO_THETA_RANGE) / TRIGO_THETA_RANGE) * (2 * math.pi)
        sin_theo[index] = amplitude * np.sin(theo_value)
        cos_theo[index] = amplitude * np.cos(theo_value)
        index += 1
    index_v = index_v
    mymatrix = np.vstack([mymatrix, np.transpose(sin_theo)])
    mymatrix = np.vstack([mymatrix, np.transpose(cos_theo)])
    mymatrix = np.vstack([mymatrix, np.transpose(sin_table)])
    mymatrix = np.vstack([mymatrix, np.transpose(cos_table)])

    error_th_osc = mymatrix[Columns.THEO_SIN] - mymatrix[Columns.OSC_SIN]
    error_th_tab = mymatrix[Columns.THEO_SIN] - mymatrix[Columns.TAB_SIN]
    error_tab_osc = mymatrix[Columns.THEO_SIN] - mymatrix[Columns.OSC_SIN]

    graphrange = 4096

    plot = MyPlot(3, 1, 1, "sin", index_v[0:graphrange], mymatrix[Columns.OSC_SIN][0:graphrange], mymatrix[Columns.THEO_SIN][0:graphrange],
                  mymatrix[Columns.TAB_SIN][0:graphrange])
    MyPlot(3, 1, 2, "error", index_v[0:graphrange], error_th_osc[0:graphrange])

    MyPlot(3, 1, 3, "error", index_v[0:graphrange], mymatrix[Columns.OSC_SIN][0:graphrange], mymatrix[Columns.THEO_SIN][0:graphrange], error_th_osc[0:graphrange])

    plot.show()


if len(sys.argv) >= 2:
    if sys.argv[1] == "file":
        sinCosTestCsv(sys.argv[2])
    elif sys.argv[1] == "simple":
        sinCosTest(SIMTABDIM, 2 ** TRIGO_SHIFT)
    else:
        runTest()
