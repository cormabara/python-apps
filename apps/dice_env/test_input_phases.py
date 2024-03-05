import math
import numpy as np

from my_trigo import trigo_dir_clarke, trigo_dir_clarke_v
from my_types import S32_MAX, S32_MIN
from report import MyReport
from tools import MyPlot, rmsval, rmsvalfrompk

AMPLITUDE = 500
SAMPLES = 100
in_s = np.arange(0, (8 * math.pi),(8 * math.pi)/SAMPLES)
# sin_theo = amplitude_ * np.sin(in_s)
# cos_theo = amplitude_ * np.cos(in_s)

MyReport("../../data","phase.txt")

phR = AMPLITUDE * np.sin(in_s)
phS = AMPLITUDE * np.sin(in_s - ((2 * math.pi) / 3))
phT = AMPLITUDE * np.sin(in_s - ((4 * math.pi) / 3))

phRS = phS - phR
phST = phT - phS

minR = np.max(phR)
maxR = np.max(phR)
rmsR = rmsval(phR)

minRS = np.max(phRS)
maxRS = np.max(phRS)
rmsRS = rmsval(phRS)

thetaR_deg = np.rad2deg(abs(np.sin(phR / AMPLITUDE)))
thetaRS_deg = np.rad2deg(abs(np.sin(phRS / maxRS)))
delta_theta_deg = (abs(thetaRS_deg[0]) - abs(thetaR_deg[0]))

MyReport().rpt_print("Phase R max:(" + str(maxR) + ") min(" + str(minR) + ")")
MyReport().rpt_print("Phase RS max:(" + str(maxRS) + ") min(" + str(minRS) + ")")
MyReport().rpt_print("Phase R rms:(" + str( rmsR) + ")")
MyReport().rpt_print("Phase RS rms:(" + str(rmsRS) + ")" + "(" + str(rmsvalfrompk(np.max(phRS))) + ")" )
MyReport().rpt_print("Delta Theta :(" + str(delta_theta_deg) + ")")


plot = MyPlot(3, 1, 1, "phases pos", in_s, phR, phS, phT)
MyPlot(3, 1, 2, "R-S & S-T pos", in_s, phR, phRS, phST)
MyPlot(3, 1, 3, "ThetaR - ThetaRS", in_s, phR, thetaR_deg, thetaRS_deg)
plot.show()
