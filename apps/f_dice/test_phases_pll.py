"""
This module is the implementation for the PLL on input phases
"""
import sys
from random import randint
from matplotlib import pyplot as plt

from f_dice.lib.my_trigo import TRIGO_THETA_RANGE
from collections import deque

from f_dice.lib.range_limits import wrap_out_of_range
from f_dice.lib.report import rpt_open, rpt_print
from f_dice.lib.tools import MyPlot
from f_dice.modules.phases_pll import PhasesPll

rpt_open("../../", "test_phases_pll.rpt")
real_mode = False
SAMPLE_FREQUENCY_HZ = 10000
DEEP = 5 * TRIGO_THETA_RANGE
test_pll: PhasesPll = None


def newStimulus(amplitude_=0, frequency_=0):
    global test_pll
    if amplitude_ == 0:
        amplitude_ = randint(300, 500)
    if frequency_ == 0:
        frequency_ = randint(45, 55)

    print("frequency: " + str(frequency_))
    print("amplitude: " + str(amplitude_))
    test_pll.stimulus(amplitude_, frequency_)


def pllRun():
    """ This is the continuous run for the PLL, the DEEP is the deep
        of the scrolling window"""
    global test_pll
    test_pll = PhasesPll(SAMPLE_FREQUENCY_HZ, DEEP,False)

    # here we are creating sub plots
    plt.ion()
    figure = plt.figure()
    initVal = [0 for i in test_pll.display_range]

    ax_theta = figure.add_subplot(331)
    ax_theta.title.set_text("Theta in / theta out")
    ax_theta.set_ylim([-(3 / 2) * TRIGO_THETA_RANGE, (3 / 2) * TRIGO_THETA_RANGE])
    line_in_theta, = ax_theta.plot(test_pll.vector_index, initVal, label="theta in")
    line_out_theta, = ax_theta.plot(test_pll.vector_index, initVal, label="theta out")
    line_ThetaPrev, = ax_theta.plot(test_pll.vector_index, initVal)

    ax_omega = figure.add_subplot(332)
    ax_omega.title.set_text("Omega in / Omega out")
    ax_omega.set_ylim([0, 1000])
    line_omega_out, = ax_omega.plot(test_pll.vector_index, initVal, label="omega out")
    line_omega_in, = ax_omega.plot(test_pll.vector_index, initVal, label="omega in")

    ax_sin = figure.add_subplot(333)
    ax_sin.title.set_text("Sin in / sin out")
    ax_sin.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
    line_sin_in, = ax_sin.plot(test_pll.vector_index, initVal, label="sin in")
    line_sin_out, = ax_sin.plot(test_pll.vector_index, initVal, label="sin out")

    ax_mid_1 = figure.add_subplot(334)
    ax_mid_1.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
    ax_mid_1.title.set_text("CosU / CosV / CosW")
    line_cos_U, = ax_mid_1.plot(test_pll.vector_index, initVal)
    line_cos_V, = ax_mid_1.plot(test_pll.vector_index, initVal)
    line_cos_W, = ax_mid_1.plot(test_pll.vector_index, initVal)

    ax_mid_2 = figure.add_subplot(335)
    ax_mid_2.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
    ax_mid_2.title.set_text("Alpha / Beta")
    line_alpha, = ax_mid_2.plot(test_pll.vector_index, initVal)
    line_beta, = ax_mid_2.plot(test_pll.vector_index, initVal)

    ax_Ed = figure.add_subplot(336)
    ax_Ed.title.set_text("Ed")
    line_Ed, = ax_Ed.plot(test_pll.vector_index, initVal)

    ax_Eq = figure.add_subplot(337)
    ax_Eq.title.set_text("Eq")
    line_Eq, = ax_Eq.plot(test_pll.vector_index, initVal)

    ax_Effort = figure.add_subplot(338)
    ax_Effort.title.set_text("Effort")
    line_Effort, = ax_Effort.plot(test_pll.vector_index, initVal)

    vector_ThetaError = deque([float(0) for i in test_pll.display_range], maxlen=test_pll.winRange)
    ax_ThetaError = figure.add_subplot(339)
    ax_ThetaError.title.set_text("ThetaError")
    line_ThetaError, = ax_ThetaError.plot(test_pll.vector_index, initVal)
    ax_ThetaError.set_ylim([-TRIGO_THETA_RANGE / 100, TRIGO_THETA_RANGE / 100])

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)

    newStimulus(400, 50)
    index = 0
    theta_in_custom = 0
    endOfLoop = False
    while not endOfLoop:
        test_pll.vector_index.append(index)
        sample_step_custom = TRIGO_THETA_RANGE * test_pll.frequency_in / SAMPLE_FREQUENCY_HZ
        theta_in_custom = (theta_in_custom + sample_step_custom) % TRIGO_THETA_RANGE
        test_pll.Calculate(real_mode, theta_in_custom)

        test_pll.theta_in_custom_v.append(test_pll.theta_in_custom)
        test_pll.omega_in_v.append(test_pll.omega_in_rad)
        test_pll.in_sinU_v.append(test_pll.in_sinU)

        test_pll.alpha_v.append(test_pll.Alpha)
        test_pll.beta_v.append(test_pll.Beta)

        test_pll.Ed_v.append(test_pll.Ed)
        test_pll.Eq_v.append(test_pll.Eq)
        test_pll.effort_v.append(test_pll.effort)

        test_pll.theta_out_custom_v.append(test_pll.theta_out_custom)
        test_pll.omega_out_v.append(test_pll.omega_out)
        test_pll.out_sinU_v.append(test_pll.out_sinU)

        test_pll.inputCosW_v.append(test_pll.cosU)
        test_pll.inputCosV_v.append(test_pll.cosV)
        test_pll.inputCosU_v.append(test_pll.cosW)

        test_pll.theta_park_v.append(test_pll.prev_theta_out)

        WrapVal = TRIGO_THETA_RANGE / 2
        error = test_pll.theta_out_custom - test_pll.theta_in_custom
        error = error % TRIGO_THETA_RANGE
        error = wrap_out_of_range(error, -WrapVal + 1, WrapVal - 1, WrapVal)
        vector_ThetaError.append(error)

        if not index % 10000:
            newStimulus()

        if not index % 50:
            line_in_theta.set_ydata(test_pll.theta_in_custom_v)
            line_out_theta.set_ydata(test_pll.theta_out_custom_v)

            line_omega_out.set_ydata(test_pll.omega_out_v)
            line_omega_in.set_ydata(test_pll.omega_in_v)

            line_sin_in.set_ydata(test_pll.in_sinU_v)
            line_sin_out.set_ydata(test_pll.out_sinU_v)

            line_cos_U.set_ydata(test_pll.inputCosU_v)
            line_cos_V.set_ydata(test_pll.inputCosV_v)
            line_cos_W.set_ydata(test_pll.inputCosW_v)

            line_alpha.set_ydata(test_pll.alpha_v)
            line_beta.set_ydata(test_pll.beta_v)

            ax_Ed.set_ylim([0, max(test_pll.Ed_v)*3/2])
            ax_Eq.set_ylim([min(test_pll.Eq_v)*3/2, max(test_pll.Eq_v)*3/2])
            line_Ed.set_ydata(test_pll.Ed_v)
            line_Eq.set_ydata(test_pll.Eq_v)

            ax_Effort.set_ylim([-max(test_pll.effort_v) * 3 / 2, max(test_pll.effort_v) * 3 / 2])
            line_Effort.set_ydata(test_pll.effort_v)

            line_ThetaPrev.set_ydata(test_pll.theta_park_v)
            line_ThetaError.set_ydata(vector_ThetaError)

            # drawing updated values
            figure.canvas.draw()
            figure.canvas.flush_events()

        index = index + 1


def pllLoop():
    global test_pll
    test_pll = PhasesPll(SAMPLE_FREQUENCY_HZ, DEEP)
    test_pll.CalculateLoop(real_mode,400,50)
    pll_plt = MyPlot(3, 1, 1, "Theta", test_pll.input_sequence_v, test_pll.theta_in_custom_v, test_pll.theta_out_custom_v, test_pll.theta_park_v)
    MyPlot(3, 1, 2, "Omega", test_pll.input_sequence_v, test_pll.omega_out_v, test_pll.omega_in_v)
    MyPlot(3, 1, 3, "Sin", test_pll.input_sequence_v, test_pll.out_sinU_v, test_pll.in_sinU_v)
    pll_plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)
    pll_plt.show()



if len(sys.argv) >= 2:
    if sys.argv[1] == "loop":
        pllLoop()
    elif sys.argv[1] == "run":
        pllRun()
    else:
        rpt_print("no mode defined")
