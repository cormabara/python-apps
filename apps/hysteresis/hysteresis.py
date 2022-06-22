# This is hysteresis simulation

import sys
sys.path.insert(1, sys.path[5] + '../personal-packages/')

import numpy as np

import matplotlib.pyplot as plot
from  import rpt_open, rpt_print_d, rpt_print


print("sys paths: ")
print(sys.path[5])
MAX_SPEED = 1400 		# max range value
MIN_SPEED = 0			# min range value

MAX_EDGE = 1000 		# max edge
MIN_EDGE = 400 		# min edge

HIST_SHIFT = 0			# right shift to calculate hysteresis 


max_speed_iu = (MAX_SPEED/60)*256
max_edge_iu = (MAX_EDGE/60)*256
min_edge_iu = (MIN_EDGE/60)*256

OUTPUT_LO = 0
OUTPUT_HI = max_speed_iu


def iu_2_rpm(iu_):
	return (iu_*60)/256

def rpm_2_iu(rpm_):
	return (rpm_/60)*256



rpt_open()
rpt_print("CALCULATION OF HYSTERESIS \n")

rpt_print("min edge[iu] is (" + str(min_edge_iu) + ") - min edge[rpm] is (" + str(iu_2_rpm(min_edge_iu)) + ")\n")
rpt_print("max edge[iu] is (" + str(max_edge_iu) + ") - max edge[rpm] is (" + str(iu_2_rpm(max_edge_iu)) + ")\n")

# hysteresis is 1/x of the useful interval
if HIST_SHIFT != 0:
	hist_iu = (int(((max_edge_iu - min_edge_iu)/2))>>HIST_SHIFT)
else:
	hist_iu = 0

rpt_print("hysteresis[iu] is (" + str(hist_iu) + ") - hiysteresis[rpm] is (" + str(iu_2_rpm(hist_iu)) + "\n")

min_edge_lo_iu = min_edge_iu - hist_iu
min_edge_hi_iu = min_edge_iu + hist_iu
rpt_print("min_edge_lo[iu](" + str(min_edge_lo_iu) + ") min_edge_hi[iu](" + str(min_edge_hi_iu) + ")")
rpt_print("min_edge_lo[rpm](" + str(iu_2_rpm(min_edge_lo_iu)) + ") min_edge_hi[rpm](" + str(iu_2_rpm(min_edge_hi_iu)) + ")")

max_edge_lo_iu = max_edge_iu - hist_iu
max_edge_hi_iu = max_edge_iu + hist_iu
rpt_print("max_edge_lo[iu](" + str(max_edge_lo_iu) + ") max_edge_hi[iu](" + str(max_edge_hi_iu) + ")")
rpt_print("max_edge_lo[rpm](" + str(iu_2_rpm(max_edge_lo_iu)) + ") max_edge_hi[rpm](" + str(iu_2_rpm(max_edge_hi_iu)) + ")")

#Se uscita alta spegno se sono sopra max + hist e sotto min - hist
def calculate_out(speed_iu_, outval_):

	if outval_ == OUTPUT_HI and ( (speed_iu_ > max_edge_hi_iu) or (speed_iu_ < min_edge_lo_iu) ):
		return OUTPUT_LO
	elif outval_ == OUTPUT_LO and ( (speed_iu_ > min_edge_hi_iu) and (speed_iu_ < max_edge_lo_iu) ):
		return OUTPUT_HI

	return outval_


time = np.arange(0, 1000, 1); # Get x values of the sine wave
speed_iu   = max_speed_iu/2 + (max_speed_iu/2)*np.sin(time/100) # Amplitude of the sine wave is sine of a variable like time

speed_output = [OUTPUT_LO for i in time+1]

for index in time-1:
	speed_output[index+1] = calculate_out(speed_iu[index+1], speed_output[index])
	rpt_print("speed[iu] (" + str(speed_iu[index]) + ")")
	# value_if_true if condition else value_if_false
	rpt_print("output is (" + ( "OFF" if speed_output[index] == OUTPUT_LO else "ON") + ")")



plot.title('Sine wave') # Give a title for the sine wave plot
plot.xlabel('Time') # Give x axis label for the sine wave plot
plot.ylabel('speed_iu = sin(time)') # Give y axis label for the sine wave plot
plot.grid(True, which='both')

plot.axhline(y=max_edge_iu, color='k')
plot.axhline(y=max_edge_hi_iu, color='g', linestyle='dashed')
plot.axhline(y=max_edge_lo_iu, color='g', linestyle='dashed')

plot.axhline(y=min_edge_iu, color='k')
plot.axhline(y=min_edge_hi_iu, color='g', linestyle='dashed')
plot.axhline(y=min_edge_lo_iu, color='g', linestyle='dashed')

plot.plot(time, speed_iu,'y') # Plot a sine wave using time and amplitude obtained for the sine wave
plot.plot(time, speed_output,'r') # Plot a sine wave using time and amplitude obtained for the sine wave

plot.show()

# Display the sine wave

#plot.show()








