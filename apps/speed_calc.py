encpulses = 1024
frequency = 5000

for speed_iter_rpm in range(1,10):
	speed_rps256 = (speed_iter_rpm/60)*256
	speed_ts = (speed_rps256*encpulses)/frequency
	print("speedrpm: " + str(speed_iter_rpm) + " -\t speed_rps256: " + str(speed_rps256) + " -\tspeed_ts: " + str(speed_ts))  
