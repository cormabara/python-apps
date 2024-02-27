""" Modulo di test per AFE con 2 modalita':
    - run: modalità normale con sequenza fissa
    - loop: loop a scorrimento """
import math
import sys
from collections import deque

import numpy as np
from matplotlib import pyplot as plt

from apps.f_dice.afe_rectifier import AfeRectifier
from my_errors import SysErr
from report import MyReport
from tools import MyPlot, CnfAfe


def run():
    NUM_WAVES = CnfAfe().WIN_DEEP / CnfAfe().PERIOD_IN_SAMPLES
    in_s = np.arange(0, (NUM_WAVES * 2 * math.pi), (NUM_WAVES * 2 * math.pi) / CnfAfe().WIN_DEEP)
    ph1 = CnfAfe().AMPLITUDE * np.sin(in_s)
    ph2 = CnfAfe().AMPLITUDE * np.sin(in_s - ((2 * math.pi) / 3))
    ph3 = CnfAfe().AMPLITUDE * np.sin(in_s - ((4 * math.pi) / 3))

    afe = AfeRectifier()
    afe.start()

    for smpl in range(0, len(in_s)):
        afe.execute(ph1[smpl], ph2[smpl], ph3[smpl])
        afe.plot_sample()
        if SysErr().check_alarm():
            MyReport().rpt_print("KILLING APPLICATION")
            break

    plot = MyPlot(4, 1, 1, "phases in", in_s, ph1, ph2, ph3)
    MyPlot(4, 1, 2, "R / R-S / S-T", in_s, ph1, afe.vmains.in_ST_v, afe.vmains.in_RT_v)
    MyPlot(4, 1, 3, "PLL R/S/T", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.in_s_v, afe.vmains.pll.in_t_v)
    #    MyPlot(4, 1, 3, "R / R-S / S-T", in_s, afe.vmains.in_RS_v, afe.vmains.linein.zc_RS_trig_v,
    #           afe.vmains.linein.fail_phases_v)
    #    MyPlot(4, 1, 4, "R / R-S / S-T", in_s, afe.vmains.in_ST_v, afe.vmains.linein.zc_ST_trig_v,
    #           afe.vmains.linein.fail_phases_v)
    plot.show()

    plot = MyPlot(4, 1, 1, "PLL R/S/T", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.in_s_v, afe.vmains.pll.in_t_v)
    MyPlot(4, 1, 2, "PLL alpha/beta", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.alpha_v, afe.vmains.pll.beta_v)
    MyPlot(4, 1, 3, "PLL ed /eq", in_s, afe.vmains.pll.ed_v, afe.vmains.pll.eq_v)
    MyPlot(4, 1, 4, "PLL theta out", in_s, afe.vmains.pll.theta_out_custom_v, afe.vmains.pll.omega_out_v)
    plot.show()

    plot = MyPlot(2, 1, 1, "PLL theta out", in_s, afe.vmains.pll.in_r_v,
                  (np.array(afe.vmains.pll.theta_out_custom_v) + afe.vmains.get_theta_out_range() / 2) % afe.vmains.get_theta_out_range())
    plot.show()

    MyReport().rpt_print("End of script")


def loop():
    ph1_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
    ph2_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
    ph3_v = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    """ This is the continuous run for the PLL, the DEEP is the deep
        of the scrolling window"""
    afe = AfeRectifier()
    afe.start()

    # here we are creating sub plots
    plt.ion()
    figure = plt.figure()
    init_val = [0 for i in CnfAfe().display_range()]
    vector_index = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    ax_input = figure.add_subplot(311)
    ax_input.title.set_text("Inputs R/S/T")
    line_in_ph1, = ax_input.plot(vector_index, init_val, label="ph1")
    line_in_ph2, = ax_input.plot(vector_index, init_val, label="ph2")
    line_in_ph3, = ax_input.plot(vector_index, init_val, label="ph3")
    ax_input.set_ylim(-3 / 2 * CnfAfe().AMPLITUDE, 3 / 2 * CnfAfe().AMPLITUDE)
    plt.grid()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)

    ax_sg = figure.add_subplot(312)
    ax_sg.title.set_text("Inputs R-S/S-T")
    line_in_ST, = ax_sg.plot(vector_index, init_val, label="ph1")
    line_in_RT, = ax_sg.plot(vector_index, init_val, label="ph2")
    ax_sg.set_ylim(-3 * CnfAfe().AMPLITUDE, 3 * CnfAfe().AMPLITUDE)
    plt.grid()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)

    ax_vmains_zc = figure.add_subplot(313)
    ax_vmains_zc.title.set_text("ZEROCROSS")
    line_in_trig_zc_rs, = ax_vmains_zc.plot(vector_index, init_val, label="trig zc RS")
    line_in_trig_zc_st, = ax_vmains_zc.plot(vector_index, init_val, label="trig zc RS")
    ax_vmains_zc.set_ylim(-3 / 2 * CnfAfe().AMPLITUDE, 3 / 2 * CnfAfe().AMPLITUDE)
    plt.grid()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)

    glbl_index = 0
    theta_in_custom = 0
    endOfLoop = False
    offset1 = offset2 = offset3 = 0
    while not endOfLoop:
        # calcolo lo step sul theta partendo dalla frequenza base e dalla frequenza di campionamento
        theta_step_custom = CnfAfe().TRIGO_THETA_RANGE * (CnfAfe().INPUT_FREQ_HZ / CnfAfe().SAMPLE_FREQUENCY_HZ)
        theta_in_custom = (theta_in_custom + theta_step_custom) % CnfAfe().TRIGO_THETA_RANGE
        # costruisco i tre angoli che mi servono per lo sfasamento di test
        theta_in_custom1 = theta_in_custom + offset1
        theta_in_custom2 = theta_in_custom + offset2
        theta_in_custom3 = theta_in_custom + offset3
        # if not glbl_index % 673:
        #    offset1 -= 100
        # if not glbl_index % 773:
        #    offset1 += 100

        # creo le tre forme di ingresso per il theta calcolato
        ph1 = CnfAfe().AMPLITUDE * math.sin(theta_in_custom1)
        ph2 = CnfAfe().AMPLITUDE * math.sin(theta_in_custom2 - ((2 * math.pi) / 3))
        ph3 = CnfAfe().AMPLITUDE * math.sin(theta_in_custom3 - ((4 * math.pi) / 3))

        afe.execute(ph1, ph2, ph3)  # esecuzione dell'afe sotto irq
        afe.plot_sample()  # Aggironamento dei vettori per il plot

        # Aggiungo i campioni delle tre forme di ingresso
        ph1_v.append(ph1)
        ph2_v.append(ph2)
        ph3_v.append(ph3)

        # Aggiorno i subplot
        line_in_ph1.set_ydata(ph1_v)
        line_in_ph2.set_ydata(ph2_v)
        line_in_ph3.set_ydata(ph3_v)

        line_in_ST.set_ydata(afe.vmains.in_ST_v)
        line_in_RT.set_ydata(afe.vmains.in_RT_v)

        line_in_trig_zc_rs.set_ydata(afe.vmains.linein.zc_RS_trig_v)
        line_in_trig_zc_st.set_ydata(afe.vmains.linein.zc_ST_trig_v)

        # drawing updated values
        if not glbl_index % 10:
            figure.canvas.draw()
            figure.canvas.flush_events()

            if not glbl_index % 100:
                afe.vmains.linein.report_debug()

        glbl_index = glbl_index + 1

        # Se ci sono allarmi nel sistema allora fermo tutto
        if SysErr().check_alarm():
            MyReport().rpt_print("KILLING APPLICATION")
            break


MyReport("../../../data", "afe_report.txt")
if len(sys.argv) >= 2:
    if sys.argv[1] == "loop":
        loop()
    elif sys.argv[1] == "run":
        run()
    else:
        MyReport().rpt_print("no mode defined")
