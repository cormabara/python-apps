import numpy as np
from mb_common_lib.report import rpt_open, rpt_print,rpt_sep
from power import Simulate, CalculateSingle, InMData, OutMDataTheo
import pandas
import sys

from tkinter.filedialog import askopenfilename

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rpt_open("")

    if len(sys.argv) == 1:
        data = np.array([
            3383,       # cmp_u
            3854,       # cmp_v
            282,       # i_m_vbus_V
            39,      # i_m_iurms_LSB
            4368,      # i_m_vdref_LSB
            3649,      # i_m_idfbk_LSB
            51,      # i_m_vqref_LSB
            48,      # i_m_iqfbk_LSB
        ])
        # filename = askopenfilename(defaultextension='.osc.csv')
        # if not filename:
        #     exit(1)
        CalculateSingle(data)
    elif len(sys.argv) == 2 and sys.argv[1]:
        filename = sys.argv[1]
        rpt_print("\nSIMULATE FROM FILE: " + filename)
        data = pandas.read_csv(filename, usecols=[0,1,2,3,4,5,6,7], header=12).to_numpy()
        powerData = Simulate(data)
        powerData.Means()
        powerData.GraphPowers()
