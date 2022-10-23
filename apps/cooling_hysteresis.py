# This is hysteresis simulation

import sys
sys.path.insert(1, sys.path[5] + '../tools/')

sys.path.append("../tools")

import numpy as np

import matplotlib.pyplot as plot
from  report import rpt_open, rpt_print_d, rpt_print

if len(sys.argv) < 3:
	print("Cooling Hysteresis needs 3 parameters:"
		  "- Temperature edge for IGBT [°C]"
		  "- Temperature edge for the motor [°C]"
		  "- Low Histeresis [°C]");
	exit(1)

min_temp = 0		# min range value
max_temp = 210		# max range value


igbt_edge = int(sys.argv[1]) 		# min edge
motor_edge = int(sys.argv[2])		# max edge
hyst_low = int(sys.argv[3])		# low hysteresis for the turn off
igbt_edge_on = igbt_edge
igbt_edge_off = igbt_edge - hyst_low;
motor_edge_on = motor_edge
motor_edge_off = motor_edge - hyst_low;



OUTPUT_LO = 0
OUTPUT_HI = max_temp/2


rpt_open()
rpt_print("CALCULATION OF OUTPUT LOW HYSTERESIS ALGORITHM \n")


rpt_print("output calculation for:")
rpt_print("igbt edge[°C]: (" + str(igbt_edge) + ")")
rpt_print("motor edge[°C]: (" + str(motor_edge) + ")")
rpt_print("hysteresis[°C]: (" + str(hyst_low) + ")")

rpt_print("igbt edge_on[°C]: (" + str(igbt_edge_on) + ")")
rpt_print("igbt edge_off[°C]: (" + str(igbt_edge_off) + ")\n")
rpt_print("motor edge_on[°C]: (" + str(motor_edge_on) + ")")
rpt_print("motor edge_off[°C]: (" + str(motor_edge_off) + ")\n")

time = np.arange(0, 1000, 1) # Get x values of the sine wave
igbt_temperature   = max_temp/2 + (max_temp/2)*np.sin(time/100) # Amplitude of the sine wave is sine of a variable like time
mot_temperature   = max_temp/2 + (max_temp/2)*np.sin((time-(time/4))/100) # Amplitude of the sine wave is sine of a variable like time
output = [OUTPUT_LO for i in time+1]



#Se uscita alta spegno se sono sopra max + hist e sotto min - hist
def calculate_out(oldout_, index_):

	if oldout_ == OUTPUT_LO:
		if igbt_temperature[index_] >= igbt_edge_on or mot_temperature[index_] >= motor_edge_on:
			return OUTPUT_HI

	else:
		if igbt_temperature[index_] < igbt_edge_off and mot_temperature[index_] < motor_edge_off:
			return OUTPUT_LO
		
	return oldout_


for index in time-1:
	output[index+1] = calculate_out(output[index],index+1)


plot.title('Sine wave') # Give a title for the sine wave plot
plot.xlabel('Time') # Give x axis label for the sine wave plot
plot.ylabel('temperature = sin(time)') # Give y axis label for the sine wave plot
plot.grid(True, which='both')

if igbt_edge != 0:
	plot.axhline(y=igbt_edge_on, color='y', linestyle='dashed', label="igbt edge on")
	plot.axhline(y=igbt_edge_off, color='y', linestyle='dashed')
	plot.plot(time, igbt_temperature,'y') # Plot a sine wave using time and amplitude obtained for the sine wave

if motor_edge != 0:
	plot.axhline(y=motor_edge_on, color='g', linestyle='dashed')
	plot.axhline(y=motor_edge_off, color='g', linestyle='dashed')
	plot.plot(time, mot_temperature,'g') # Plot a sine wave using time and amplitude obtained for the sine wave

plot.plot(time, output,'r') # Plot a sine wave using time and amplitude obtained for the sine wave
plot.legend(("igbt edge off", "igbt edge on","igbt temperature", "motor edge off", "motor edge on","motor temperature","output"))
plot.show()

# Display the sine wave

#plot.show()








