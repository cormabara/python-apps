from mb_common_lib import report
from mb_dice_lib.iir_filter import IIRFilter
import matplotlib.pyplot as plt

FCUTMHZ = 200
FSAMHZ = 100
START_VAL = 0
TARGET_VAL = 2000
TIME_MS = (1 / FSAMHZ) * 1000


def Test_Filter(path_="./"):
    report.rpt_open(path_)
    report.rpt_print("this is a test for report file")
    tstFilter = IIRFilter(FCUTMHZ, FSAMHZ)
    tstFilter.Preset(START_VAL)
    times = [0]
    samples = [START_VAL]

    while samples[-1] < TARGET_VAL * 95 / 100:
        times.append(times[-1] + (TIME_MS / 1000))
        samples.append(tstFilter.Filter(TARGET_VAL))

    report.rpt_print("IIR Filter test")
    tmp = plt.subplot(1, 1, 1)
    plt.grid(color='0.95')
    plt.plot(times, samples, 'm', label="output")
    tmp.set_xlabel("time[s]")
    tmp.set_ylabel("value")
    plt.legend(title='Legend')

    plt.show()

    report.rpt_sep()
    report.rpt_close()


Test_Filter()
