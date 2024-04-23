""" Modulo di test per AFE con 2 modalita':
    - run: modalità normale con sequenza fissa
    - loop: loop a scorrimento """
import math
import sys
from collections import deque
import numpy as np
from matplotlib import pyplot as plt

from afe_rectifier import AfeRect, AfeRectSt
from afe_config import CnfAfe, AfeSignals
from my_errors import SysErr
from report import MyReport
from tools import MyPlot


class LoopPlotterFigure:

    class LoopPlotterSubplot:

        def __init__(self,pos_,subplot_,title_, label1_,label2_=None,label3_=None,label4_=None):
            self.subplot = subplot_
            self.subplot.title.set_text(title_)
            self.init_val = [0 for i in CnfAfe().display_range()]
            self.vector_index = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

            self.line_1 = None
            self.line_2 = None
            self.line_3 = None
            self.line_4 = None
            self.pos = pos_

            if label1_:
                self.line_1, = self.subplot.plot(self.vector_index, self.init_val, label=label1_, color="red")
            if label2_:
                self.line_2, = self.subplot.plot(self.vector_index, self.init_val, label=label2_, color="blue")
            if label3_:
                self.line_3, = self.subplot.plot(self.vector_index, self.init_val, label=label3_, color="green")
            if label4_:
                self.line_4, = self.subplot.plot(self.vector_index, self.init_val, label=label4_, color="yellow")

            self.subplot.legend()

        def set_y_range(self,min_,max_):
            self.subplot.set_ylim(min_, max_)

        def add_samples(self, queue1_, queue2_, queue3_, queue4_):
            if self.line_1:
                self.line_1.set_ydata(queue1_)
            if self.line_2:
                self.line_2.set_ydata(queue2_)
            if self.line_3:
                self.line_3.set_ydata(queue3_)
            if self.line_4:
                self.line_4.set_ydata(queue4_)

    def __init__(self,plt_):
        self.plt = plt_
        self.subplots = list()
        self.figure = self.plt.figure()

    def add_subplot(self,pos_,title_, label1_,label2_=None,label3_=None,label4_=None):
        subplot = self.figure.add_subplot(pos_)
        lsp = self.LoopPlotterSubplot(pos_,subplot,title_, label1_,label2_,label3_,label4_)

        self.subplots.append(lsp)
        self.plt.grid()
        self.plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)

    def add_samples(self, pos_, queue1_, queue2_=None, queue3_=None, queue4_=None):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1:
            res[0].add_samples(queue1_, queue2_, queue3_, queue4_)

    def refresh(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def set_subplot_range(self, pos_,  min_, max_):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1:
            res[0].set_y_range(min_,max_)

def run():
    afe = AfeRect()
    afe.status = AfeRectSt.aferest_st_start
    for smpl in range(0, len(AfeSignals().ph1_v)):
        AfeSignals().generate_phases_in()
        afe.handle(AfeSignals().in_rs_lsb, AfeSignals().in_ts_lsb)  # esecuzione dell'afe sotto irq
        afe.plot_sample()
        #if SysErr().check_alarm():
        #    MyReport().rpt_print("KILLING APPLICATION")
        #    break

    in_s = np.array([ii for ii in CnfAfe().display_range()])
    plot = MyPlot(5, 1, 1, "phases in", in_s, AfeSignals().ph1_v, AfeSignals().ph2_v, AfeSignals().ph3_v)
    plot.legend()
    MyPlot(5, 1, 2, "R / R-S / S-T", in_s, AfeSignals().ph1_v, AfeSignals().plot_in_rs, AfeSignals().plot_in_ts)
    plot.legend()
    MyPlot(5, 1, 3, "PLL R/S/T", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.in_s_v, afe.vmains.pll.in_t_v)
    plot.legend()
    MyPlot(5, 1, 5, "RS / RS-trig", in_s, AfeSignals().plot_in_rs, afe.vmains.linein.zc_RS_trig_v)
    plot.legend()
    MyPlot(5, 1, 4, "TS / TS-trig", in_s, AfeSignals().plot_in_ts, afe.vmains.linein.zc_TS_trig_v)
    plot.legend()
    plot.show()

    plot = MyPlot(4, 1, 1, "PLL R/S/T", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.in_s_v, afe.vmains.pll.in_t_v)
    MyPlot(4, 1, 2, "PLL alpha/beta", in_s, afe.vmains.pll.in_r_v, afe.vmains.pll.alpha_v, afe.vmains.pll.beta_v)
    MyPlot(4, 1, 3, "PLL ed /eq", in_s, afe.vmains.pll.ed_v, afe.vmains.pll.eq_v)
    MyPlot(4, 1, 4, "PLL theta out", in_s, afe.vmains.pll.theta_out_custom_v, afe.vmains.pll.omega_out_rad_v)
    plot.show()

    plot = MyPlot(2, 1, 1, "PLL theta out", in_s, afe.vmains.pll.in_r_v,afe.vmains.pll.theta_out_custom_v)
    plot.show()

    input_fig = LoopPlotterFigure(plt)
    input_fig.add_subplot(311, "Inputs 1/2/3", "ph1", "ph2","ph3")
    input_fig.set_subplot_range(311, -CnfAfe().IN_MAXAMPLITUDE*11/10, CnfAfe().IN_MAXAMPLITUDE*11/10)
    input_fig.add_samples(311, AfeSignals().ph1_v, AfeSignals().ph2_v, AfeSignals().ph3_v)

    input_fig.add_subplot(312, "Inputs R-S/T-S", "rs", "ts")
    input_fig.set_subplot_range(312, -CnfAfe().MAX_SIGMADELTA_VAL*11/10, CnfAfe().MAX_SIGMADELTA_VAL*11/10)
    input_fig.add_samples(312, AfeSignals().plot_in_rs, AfeSignals().plot_in_ts)

    input_fig.add_subplot(313, "Inputs R/S/T", "R", "S","T")
    input_fig.set_subplot_range(313, -CnfAfe().MAX_SIGMADELTA_VAL*11/10, CnfAfe().MAX_SIGMADELTA_VAL*11/10)
    input_fig.add_samples(313, afe.vmains.linein.in_R_v, afe.vmains.linein.in_S_v, afe.vmains.linein.in_T_v)
    input_fig.refresh()
    plot.show()

    MyReport().rpt_print("End of script")


main_timer = 0


def loop():
    global main_timer

    """ This is the continuous run for the PLL, the DEEP is the deep
        of the scrolling window"""
    afe = AfeRect()

    # here we are creating sub plots
    plt.ion()

    input_fig = LoopPlotterFigure(plt)
    input_fig.add_subplot(211, "Inputs R/S/T", "ph1", "ph2","ph3")
    input_fig.set_subplot_range(211, -CnfAfe().IN_MAXAMPLITUDE*11/10, CnfAfe().IN_MAXAMPLITUDE*11/10)
    input_fig.add_subplot(212, "Inputs R-S/T-S", "rs", "ts")
    input_fig.set_subplot_range(212, -CnfAfe().MAX_SIGMADELTA_VAL*20/10, CnfAfe().MAX_SIGMADELTA_VAL*20/10)

    linein_fig = LoopPlotterFigure(plt)
    linein_fig.add_subplot(211, "Zerocross", "trig zc RS", "target_ref")
    linein_fig.set_subplot_range(211, -5, 500)
    linein_fig.add_subplot(212, "R / S / T", "R", "S", "T")
    linein_fig.set_subplot_range(212, -2000, 2000)


    pll_fig = LoopPlotterFigure(plt)
    pll_fig.add_subplot(311, "alpha/beta","phase_r", "alpha", "beta")
    pll_fig.set_subplot_range(311, -2000,2000)
    pll_fig.add_subplot(312, "ed / eq", "phase_r", "ed", "eq")
    pll_fig.set_subplot_range(312, -2000,2000)
    pll_fig.add_subplot(313, "pll output", "phase_r","theta[cust]","omega[rad]")
    pll_fig.set_subplot_range(313, -2000,2000)

    vbus_fig = LoopPlotterFigure(plt)
    vbus_fig.add_subplot(111, "vbus_pid", "target_volt", "trig zc ST")
    vbus_fig.set_subplot_range(111, -10,600)

    glbl_index = 0
    theta_in_custom = 0
    endOfLoop = False
    offset1 = offset2 = offset3 = 0

    # Questo loop fa una passata ogni 100uS
    while not endOfLoop:

        AfeSignals().generate_phases_in()

        # Gestione sotto irq, l'ingresso del rettificatore sono i due segnali differenziali
        # R-T e S-T
        afe.handle(AfeSignals().in_rs_lsb, AfeSignals().in_ts_lsb)  # esecuzione dell'afe sotto irq

        # Gestione sotto main (gestione lenta in background)
        if not main_timer:
            afe.background()
            main_timer = CnfAfe().MAIN_TIME_100uS
        else:
            main_timer -= 1

        input_fig.add_samples(211,AfeSignals().ph1_v,AfeSignals().ph2_v,AfeSignals().ph3_v)
        input_fig.add_samples(212, AfeSignals().plot_in_rs, AfeSignals().plot_in_ts)

        linein_fig.add_samples(211,afe.vmains.linein.zc_RS_trig_v,afe.vmains.linein.zc_TS_trig_v)
        linein_fig.add_samples(212,afe.vmains.pll.in_r_v,afe.vmains.pll.in_s_v,afe.vmains.pll.in_t_v)

        pll_fig.add_samples(311, afe.vmains.pll.in_r_v, afe.vmains.pll.alpha_v, afe.vmains.pll.beta_v)
        pll_fig.add_samples(312, afe.vmains.pll.in_r_v, afe.vmains.pll.ed_v, afe.vmains.pll.eq_v)
        pll_fig.add_samples(313, afe.vmains.pll.in_r_v, afe.vmains.pll.theta_out_custom_v, afe.vmains.pll.omega_out_rad_v)

        vbus_fig.add_samples(111,afe.vbus.plt_target_volt,afe.vbus.plt_reference_volt)

        # drawing updated values
        if not glbl_index % 100:
            input_fig.refresh()
            linein_fig.refresh()
            vbus_fig.refresh()


        # Se ci sono allarmi nel sistema allora fermo tutto
        if SysErr().check_alarm():
            MyReport().rpt_print("KILLING APPLICATION")
            break

        glbl_index += 1


MyReport("./", "afe_report.log")
if len(sys.argv) >= 2:
    if sys.argv[1] == "loop":
        loop()
    elif sys.argv[1] == "run":
        run()
    else:
        MyReport().rpt_print("no mode defined")
