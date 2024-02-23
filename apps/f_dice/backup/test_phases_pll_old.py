"""
This module is intended to test the phases_pll module

"""
import math

import numpy
from matplotlib import pyplot as plt

from tools import MyPlot
from phases_pll_old import PhasesPllOld
from collections import deque

import sys
stimulus = bool(sys.argv[1])
test_pll = PhasesPllOld(False)
frequency = 50
if stimulus:
    # Using a stimulus wave
    test_pll.Stimulus(20, frequency, 1000)
    plt = MyPlot(1, 1, 1, "sin", test_pll.msecRange,test_pll.sin_input, test_pll.sin_output, test_pll.sin_input-test_pll.sin_output)
    plt.show()
else:
    test_pll.ref_omega = 2 * math.pi * frequency

    endOfLoop = False
    inAngleDeg = 0
    winrange = 720
    display_range = range(0, winrange)
    inival = [float(0) for i in display_range]
    vector_index = deque([i for i in display_range],maxlen=winrange)
    vector_uu = deque(inival, maxlen=winrange)
    vector_err = deque(inival,maxlen=winrange)
    vector_factor = deque(inival,maxlen=winrange)
    vector_zz = deque(inival,maxlen=winrange)
    vector_output = deque(inival,maxlen=winrange)
    vector_deltaOmega = deque(inival,maxlen=winrange)

    # here we are creating sub plots
    plt.ion()
    figure = plt.figure()
    plt.title("Test PLL", fontsize=20)

    initVal = [0 for i in display_range]
    ax1 = figure.add_subplot(221)
    ax1.set_ylim([-1.1, 1.1])
    line1a, = ax1.plot(vector_index, initVal)
    line1b, = ax1.plot(vector_index, initVal)

    ax2 = figure.add_subplot(222)
    ax2.set_ylim([-0.1, 0.1])
    line2, = ax2.plot(vector_index, initVal)

    ax3 = figure.add_subplot(223)
    ax3.set_ylim([-2.1, 2.1])
    line3, = ax3.plot(vector_index, initVal)

    ax4 = figure.add_subplot(224)
    ax4.set_ylim([-1.1, 1.1])
    line4, = ax4.plot(vector_index, initVal)

    index = 0

    while not endOfLoop:
        vector_index.append(index)

        inAngleDeg = index % 360
        inTetaRad = numpy.deg2rad(inAngleDeg)
        test_pll.Iterate(inTetaRad)

        vector_uu.append(test_pll.uu)
        vector_err.append(test_pll.error)
        vector_output.append(test_pll.output)
        vector_deltaOmega.append(test_pll.delta_omega)
        vector_factor.append(test_pll.factor)

        if not index%10:
            line1a.set_ydata(vector_uu)
            line1b.set_ydata(vector_output)

            line2.set_ydata(vector_err)
            line3.set_ydata(vector_factor)
            lim = max(vector_deltaOmega)
            ax4.set_ylim(-lim*2, lim*2)
            line4.set_ydata(vector_deltaOmega)
            # drawing updated values
            figure.canvas.draw()
            figure.canvas.flush_events()

        index = index + 1
