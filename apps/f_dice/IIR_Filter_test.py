# This is a macro to evaluate the maximum cut frequency of a filter

import sys
from report import rpt_open, rpt_print, rpt_print_d, rpt_sep, rpt_close
from my_types import U32_MAX
from iir_filter import IIRFilter
import matplotlib.pyplot as plt

rpt_open("./iirfilter.txt")
rpt_print(sys.argv[0])
rpt_print("cut frequency 	[mHz]: " + sys.argv[1])
rpt_print("sample frequency	[Hz] : " + sys.argv[2])


cut_freq_mhz = int(sys.argv[1])
smp_freq_hz = int(sys.argv[2])
start = int(sys.argv[3])
target = int(sys.argv[4])


time_ms = (1/smp_freq_hz)*1000

iir_filter = IIRFilter(cut_freq_mhz, smp_freq_hz)
iir_filter.Preset(start)

times = [0]
samples = [start]

while samples[-1] < target*95/100:
	times.append(times[-1] + (time_ms/1000))
	samples.append(iir_filter.Filter(target))



print("Filter")
tmp = plt.subplot(1, 1, 1)
plt.grid(color='0.95')
plt.plot(times, samples, 'm', label="output")
tmp.set_xlabel("time[s]")
tmp.set_ylabel("value")
plt.legend(title='Legend')

plt.show()
