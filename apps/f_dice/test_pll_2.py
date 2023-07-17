"""
This module is the second implementation for the PLL on input phases
"""
import math
from random import random, randint

import keyboard
import numpy
from matplotlib import pyplot as plt

from f_dice.lib.my_trigo import TRIGO_THETA_RANGE
from f_dice.lib.tools import MyPlot
from f_dice.modules.pll_1 import PhasesPll
from collections import deque

from f_dice.modules.pll_2 import Pll_2

real_mode = True
SAMPLE_FREQUENCY_HZ = 40000
BASE_FREQUENCY = 50
DEEP = 5 * (2 * math.pi)
test_pll = Pll_2(SAMPLE_FREQUENCY_HZ, DEEP)
step_rad = 2 * math.pi * BASE_FREQUENCY / SAMPLE_FREQUENCY_HZ

winRange = int(4 * (2*math.pi)/step_rad)

display_range = range(0, winRange)
iniVal = [float(0) for i in display_range]
vector_index = deque([i for i in display_range], maxlen=winRange)

vector_sin_in = deque(iniVal, maxlen=winRange)
vector_theta_in = deque(iniVal, maxlen=winRange)
vector_omega_in = deque(iniVal, maxlen=winRange)

vector_Alpha = deque(iniVal, maxlen=winRange)
vector_Beta = deque(iniVal, maxlen=winRange)

vector_Ed = deque(iniVal, maxlen=winRange)
vector_Eq = deque(iniVal, maxlen=winRange)
vector_Effort = deque(iniVal, maxlen=winRange)
vector_cosU = deque(iniVal, maxlen=winRange)
vector_cosV = deque(iniVal, maxlen=winRange)
vector_cosW = deque(iniVal, maxlen=winRange)

vector_sin_out = deque(iniVal, maxlen=winRange)
vector_theta_out = deque(iniVal, maxlen=winRange)
vector_omega_out = deque(iniVal, maxlen=winRange)

vector_ThetaError = deque(iniVal, maxlen=winRange)

# here we are creating sub plots
plt.ion()
figure = plt.figure()

initVal = [0 for i in display_range]

ax_theta = figure.add_subplot(331)
ax_theta.title.set_text("Theta in / theta out")
ax_theta.set_ylim([-2 * math.pi * (3/2), 2 * math.pi * (3/2)])
line_in_theta, = ax_theta.plot(vector_index, initVal, label="theta in")
line_out_theta, = ax_theta.plot(vector_index, initVal, label="theta out")

ax_omega = figure.add_subplot(332)
ax_omega.title.set_text("Omega in / Omega out")
ax_omega.set_ylim([0, 1000])
line_omega_out, = ax_omega.plot(vector_index, initVal, label="omega out")
line_omega_in, = ax_omega.plot(vector_index, initVal, label="omega in")

ax_sin = figure.add_subplot(333)
ax_sin.title.set_text("Sin in / sin out")
ax_sin.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
line_sin_in, = ax_sin.plot(vector_index, initVal, label="sin in")
line_sin_out, = ax_sin.plot(vector_index, initVal, label="sin out")

ax_mid_1 = figure.add_subplot(334)
ax_mid_1.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
ax_mid_1.title.set_text("CosU / CosV / CosW")
line_cos_U, = ax_mid_1.plot(vector_index, initVal)
line_cos_V, = ax_mid_1.plot(vector_index, initVal)
line_cos_W, = ax_mid_1.plot(vector_index, initVal)

ax_mid_2 = figure.add_subplot(335)
ax_mid_2.set_ylim([-2 ** test_pll.ADC_NUMBITS, 2 ** test_pll.ADC_NUMBITS])
ax_mid_2.title.set_text("Alpha / Beta")
line_alpha, = ax_mid_2.plot(vector_index, initVal)
line_beta, = ax_mid_2.plot(vector_index, initVal)

ax_Ed = figure.add_subplot(336)
ax_Ed.title.set_text("Ed")
line_Ed, = ax_Ed.plot(vector_index, initVal)

ax_Eq = figure.add_subplot(337)
ax_Eq.title.set_text("Eq")
line_Eq, = ax_Eq.plot(vector_index, initVal)

ax_Effort = figure.add_subplot(338)
ax_Effort.title.set_text("Effort")
line_Effort, = ax_Effort.plot(vector_index, initVal)

ax_ThetaError = figure.add_subplot(339)
ax_ThetaError.title.set_text("ThetaError")
line_ThetaError, = ax_ThetaError.plot(vector_index, initVal)
ax_ThetaError.set_ylim([-0.1, 0.1])

index = 0
theta_in_rad = 0


def newStimulus(amplitude_, frequency_):
    test_pll.stimulus(amplitude_, frequency_)


stimulus_amplitude = 1
stimulus_frequency = 1

newStimulus(stimulus_amplitude, stimulus_frequency)

endOfLoop = False
while not endOfLoop:
    vector_index.append(index)
    sample_step_rad = 2 * math.pi * test_pll.frequency_in / SAMPLE_FREQUENCY_HZ
    theta_in_rad = (theta_in_rad + sample_step_rad) % (2*math.pi)
    test_pll.Calculate(real_mode, theta_in_rad)

    vector_theta_in.append(test_pll.theta_in_rad)
    vector_omega_in.append(test_pll.omega_in_rad)
    vector_sin_in.append(test_pll.in_sinU)

    vector_Alpha.append(test_pll.Alpha)
    vector_Beta.append(test_pll.Beta)

    vector_Ed.append(test_pll.Ed)
    vector_Eq.append(test_pll.Eq)
    vector_Effort.append(test_pll.effort)

    vector_theta_out.append(test_pll.theta_out_rad)
    vector_omega_out.append(test_pll.omega_out)
    vector_sin_out.append(test_pll.out_sinU)

    vector_cosU.append(test_pll.cosU)
    vector_cosV.append(test_pll.cosV)
    vector_cosW.append(test_pll.cosW)

    error = test_pll.theta_out_rad - test_pll.theta_in_rad
    vector_ThetaError.append(error)

    if not index % 5000:
        stimulus_amplitude = randint(80, 100)
        stimulus_frequency = randint(45, 55)
        print("frequency: " + str(stimulus_frequency))
        print("amplitude: " + str(stimulus_amplitude))
        newStimulus(stimulus_amplitude, stimulus_frequency)

    if not index % 50:
        line_in_theta.set_ydata(vector_theta_in)
        line_out_theta.set_ydata(vector_theta_out)

        line_omega_out.set_ydata(vector_omega_out)
        line_omega_in.set_ydata(vector_omega_in)

        line_sin_in.set_ydata(vector_sin_in)
        line_sin_out.set_ydata(vector_sin_out)

        line_cos_U.set_ydata(vector_cosU)
        line_cos_V.set_ydata(vector_cosV)
        line_cos_W.set_ydata(vector_cosW)

        line_alpha.set_ydata(vector_Alpha)
        line_beta.set_ydata(vector_Beta)

        ax_Ed.set_ylim([0, max(vector_Ed)*3/2])
        ax_Eq.set_ylim([min(vector_Eq)*3/2, max(vector_Eq)*3/2])

        line_Ed.set_ydata(vector_Ed)
        line_Eq.set_ydata(vector_Eq)

        ax_Effort.set_ylim([min(vector_Effort) * 3 / 2, max(vector_Effort) * 3 / 2])
        line_Effort.set_ydata(vector_Effort)

        line_ThetaError.set_ydata(vector_ThetaError)

        # drawing updated values
        figure.canvas.draw()
        figure.canvas.flush_events()


    index = index + 1
