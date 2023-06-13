# This is hysteresis simulation


# Add the path for the libs
import sys
sys.path.append("../tools")

import numpy as np

import matplotlib.pyplot as plot
from  report import rpt_open, rpt_print_d, rpt_print

if len(sys.argv) < 3:
	print("Hysteresis needs 3 parameters:"
		  "- Min speed [RPM]"
		  "- Max speed [RPM]"
		  "- Low Histeresis [RPM]");
	exit(1)


min_edge_rpm = int(sys.argv[1]) 		# min edge
max_edge_rpm = int(sys.argv[2])		# max edge

hyst_low_rpm = int(sys.argv[3])		# low hysteresis for the turn off

min_speed_rpm = 0		# min range value
max_speed_rpm = max_edge_rpm * 2		# max range value


max_speed_iu = (max_speed_rpm / 60) * 256
max_edge_iu = (max_edge_rpm / 60) * 256
min_edge_iu = (min_edge_rpm / 60) * 256

OUTPUT_LO = 0
OUTPUT_HI = max_speed_iu


def iu_2_rpm(iu_):
	return (iu_*60)/256

def rpm_2_iu(rpm_):
	return (rpm_/60)*256



rpt_open()
rpt_print("CALCULATION OF OUTPUT LOW HYSTERESIS ALGORITHM \n")

# hysteresis is 1/x of the useful interval
# if HIST_SHIFT != 0:
# 	hist_iu = (int(((max_edge_iu - min_edge_iu)/2))>>HIST_SHIFT)
# else:
hist_iu = rpm_2_iu(hyst_low_rpm)

rpt_print("output calculation for:")
rpt_print("min edge[rpm]: (" + str(iu_2_rpm(min_edge_iu)) + ") - min edge[iu]: (" + str(min_edge_iu) + ")\n")
rpt_print("max edge[rpm]: (" + str(iu_2_rpm(max_edge_iu)) + ") - max edge[iu]: (" + str(max_edge_iu) + ")\n")
rpt_print("hysteresis[rpm] is (" + str(iu_2_rpm(hist_iu)) + ") - hiysteresis[rpm] is (" + str(hist_iu) + "\n")

if min_edge_iu != 0:
	rpt_print("")
	min_edge_lo_iu = min_edge_iu - hist_iu
	min_edge_hi_iu = min_edge_iu + hist_iu
	rpt_print("min_edge_lo[iu](" + str(min_edge_lo_iu) + ")")
	rpt_print("min_edge_lo[rpm](" + str(iu_2_rpm(min_edge_lo_iu)) + ")")

if max_edge_iu != 0:
	rpt_print("")
	max_edge_lo_iu = max_edge_iu - hist_iu
	max_edge_hi_iu = max_edge_iu + hist_iu
	rpt_print("max_edge_lo[iu](" + str(max_edge_lo_iu) + ")")
	rpt_print("max_edge_lo[rpm](" + str(iu_2_rpm(max_edge_lo_iu)) + ")")


#Se uscita alta spegno se sono sopra max + hist e sotto min - hist
def calculate_out(speed_iu_, outval_):

	if min_edge_iu != 0 and max_edge_iu != 0:
		if outval_ == OUTPUT_HI and ( (speed_iu_ > max_edge_hi_iu) or (speed_iu_ < min_edge_lo_iu) ):
			rpt_print("OFF")
			return OUTPUT_LO
		elif outval_ == OUTPUT_LO and ( (speed_iu_ > min_edge_hi_iu) and (speed_iu_ < max_edge_lo_iu) ):
			rpt_print("ON")
			return OUTPUT_HI
	elif min_edge_iu != 0:
		if outval_ == OUTPUT_HI and speed_iu_ < min_edge_lo_iu:
			return OUTPUT_LO
		elif outval_ == OUTPUT_LO and speed_iu_ > min_edge_hi_iu:
			return OUTPUT_HI
	elif max_edge_iu != 0:
		if outval_ == OUTPUT_HI and speed_iu_ > max_edge_hi_iu:
			return OUTPUT_LO
		elif outval_ == OUTPUT_LO and speed_iu_ < max_edge_lo_iu:
			return OUTPUT_HI
		
	return outval_


time = np.arange(0, 1000, 1) # Get x values of the sine wave
speed_iu   = (max_edge_iu + min_edge_iu)/2 + (max_speed_iu/2)*np.sin(time/100) # Amplitude of the sine wave is sine of a variable like time

speed_output = [OUTPUT_LO for i in time+1]

for index in time-1:
	speed_output[index+1] = calculate_out(speed_iu[index+1], speed_output[index])
	# rpt_print("speed[iu] (" + str(speed_iu[index]) + ")")
	# value_if_true if condition else value_if_false
	# rpt_print("output is (" + ( "OFF" if speed_output[index] == OUTPUT_LO else "ON") + ")")



plot.title('Sine wave') # Give a title for the sine wave plot
plot.xlabel('Time') # Give x axis label for the sine wave plot
plot.ylabel('speed_iu = sin(time)') # Give y axis label for the sine wave plot
plot.grid(True, which='both')

if max_edge_iu != 0:
	plot.axhline(y=max_edge_iu, color='k')
	plot.axhline(y=max_edge_hi_iu, color='g', linestyle='dashed')
	plot.axhline(y=max_edge_lo_iu, color='g', linestyle='dashed')

if min_edge_iu != 0:
	plot.axhline(y=min_edge_iu, color='k')
	plot.axhline(y=min_edge_hi_iu, color='g', linestyle='dashed')
	plot.axhline(y=min_edge_lo_iu, color='g', linestyle='dashed')

plot.plot(time, speed_iu,'y') # Plot a sine wave using time and amplitude obtained for the sine wave
plot.plot(time, speed_output,'r') # Plot a sine wave using time and amplitude obtained for the sine wave

plot.show()

# Display the sine wave

#plot.show()








