"""@package
This script calculate the timestamp with the shift

- ORI: the value and resolution for the 64bit time in 10nS
- SHIFTED: the value and resolution for the 64 bit shifted until 
	second resolution is 1
- TEST: calculation with shift passed as parameter
"""

import sys

# This is the basic value to 10nS to S conversion
from_10ns_to_s = 100000000

# Maximum 64bit value for the timestamp (maximum resolution)
max_timestamp_10nS = 0xffffffffffffffff



def calc_time(timestamp_s_):
	'''
	This function calculate time in years-day-hour-minutes-seconds form a timestamp in seconds
	'''
	seconds = int(timestamp_s_%60)
	timestamp_s_ /= 60;
	minutes = int(timestamp_s_%60)
	timestamp_s_ /= 60
	hours = int(timestamp_s_%24)
	timestamp_s_ /= 24;
	days = int(timestamp_s_%365)
	timestamp_s_ /= 365;
	years = int(timestamp_s_)
	print ("time: " + str(years) + "." + str(days) + " " + str(hours) + ":" + str(minutes) + ":" + str(seconds))


def calc_resolution(shift):
	'''
	This function calculate the resolution in seconds due to a shift in the 64bit original value
	'''
	shifted = from_10ns_to_s / (1 << shift)
	return 1 / shifted


def calc_shift():
	'''
	This function calculate the maximum shift that grant 1sec resolution 
	'''
	resolution = from_10ns_to_s
	shift_cnt = 0
	while resolution != 0 and shift_cnt < 64:
		resolution >>= 1
		shift_cnt += 1
		print("shifted: (" + str(shift_cnt) + ") - (" + str(resolution) + ")")
		
	shift_cnt -= 1
	print("shift: " + str(shift_cnt))
	print("resolution: " + str(from_10ns_to_s>>shift_cnt))
	return shift_cnt


shift_optimal = calc_shift()
shift_test = int(sys.argv[1]);

max_timestamp_ori = int(max_timestamp_10nS / from_10ns_to_s)
max_timestamp_shifted = max_timestamp_10nS >> shift_optimal
max_timestamp_test = max_timestamp_10nS >> shift_test


print("TIME ORI\t\t")
print("max_timestamp_10nS: " + hex(max_timestamp_10nS));
calc_time(max_timestamp_ori)
print("TIME SHIFTED\t\t")
print("max_timestamp_shifted: " + hex(max_timestamp_shifted));
calc_time(max_timestamp_shifted)
print("TIME TEST\t\t")
print("max_timestamp_test: " + hex(max_timestamp_test));
calc_time(max_timestamp_test)
print("resolution: " + str(calc_resolution(shift_test)))


