# Gestione della conversione da unità standard rps o rps/s in iu/s o iu/s^2
# Parametri della macro:
# 1) Valore della rampa in round/s^2, se 0 scorre tutto il range di valori
# 2) Frequenza del loop: "H" loop a 100uS - "L" loop a 1ms
# 3) Fattore di shift per il calcolo dell'unità interna del trajectory (shift a dx)


import sys
import matplotlib.pyplot as plt
from mb_common_lib import types

TRAJ_AMPL_FACTOR_SHIFT = 11

PosLoop_Sample_Rate_L = 1000
PosLoop_Sample_Rate_H = 10000

MotorEncPulses = 4096

found = False

# Classe di appoggio con i valori si ingresso e uscita della funzione di conversione
class RetVal:
	def __init__(self):
		self.speed_rpm = 0
		self.acc_round_on_sec2 = 0
		self.acc_iu_on_sec2 = 0
		
		self.conv1 = 0
		self.conv2 = 0
		self.conv3 = 0
	
		self.acc_conv_a = []
		self.acc_conv_b = []

def Traj_Inc2Iu(val_):
	return val_*(2**TRAJ_AMPL_FACTOR_SHIFT)



def Conversion(value,conv_type,PosLoop_Sample_Rate):

	retval = RetVal()
	
	global found
	test = (value * MotorEncPulses);

	retval.acc_round_on_sec2 = value
	
	if test <= (types.U32_MAX >> TRAJ_AMPL_FACTOR_SHIFT):
		num = test;
		num2 = 1
	else:
		num = value;
		num2 = MotorEncPulses;

	if num2 != 1 and found == False:
		print ("(1) num is: " + str(num)+" and num2 is: " + str(num2) + "\n");
		found = True 

	retval.conv1 = num
	retval.conv2 = num2

	# Conversione del dato da increments a internal unity
	num = Traj_Inc2Iu(num);
	retval.conv3 = num

	if conv_type == 'speed_rpm':

		num = ((num / (PosLoop_Sample_Rate * 15)) * num2) >> 2		# [rpm] ==> [iu/s]
	
	elif conv_type == 'accel_rps2':									# [round/s^2] ==> [iu/s^2]

		if num2 != 1:
			num = ((num/PosLoop_Sample_Rate) * num2)/PosLoop_Sample_Rate;
		else:
			num = num/(PosLoop_Sample_Rate * PosLoop_Sample_Rate);
	
		retval.acc_conv_a.append(num)

		retval.acc_conv_b.append(num*num2)
		retval.acc_conv_b.append((num*num2)/(PosLoop_Sample_Rate * PosLoop_Sample_Rate))
		
		retval.acc_iu_on_rsec2 = retval.acc_conv_b[1]
#		print ("(2) num is: " + str(num)+"\n"); 


	elif conv_type =='jerk_rps3':									# [round/(s^3)] ==> [iu/(s^3)]:

		if num2 != 1:
			num = (num/PosLoop_Sample_Rate);
			if num < S16_MAX:
				num = (num * num2)/(PosLoop_Sample_Rate * PosLoop_Sample_Rate);
			else:
				num = ((num/PosLoop_Sample_Rate) * num2)/(PosLoop_Sample_Rate);
		else:
			num = (num * num2)/(PosLoop_Sample_Rate * PosLoop_Sample_Rate * PosLoop_Sample_Rate);

#	print ("(FINAL) num is: " + str(num)+"\n"); 
	return retval



shift = 0
conv_type = 'accel_rps2'
val_range = 1000

print(sys.argv[0])
par1 = float(sys.argv[1])
par2 = sys.argv[2]
par3 = float(sys.argv[3])

value = par1

sample_rate = PosLoop_Sample_Rate_L
if par2 == "H":
	sample_rate = PosLoop_Sample_Rate_H

TRAJ_AMPL_FACTOR_SHIFT = int(par3)


if (value == 0):
	
	inval = [i for i in range(0,val_range)]
	retval = [RetVal() for i in range(0,val_range)]
	conv1 = [i for i in range(0,val_range)]
	conv2 = [i for i in range(0,val_range)]
	conv3 = [i for i in range(0,val_range)]
	limit = [types.U32_MAX for i in range(0,val_range)]
	acc_out = [0 for i in range(0,val_range)]

	for scan in range(1,val_range):
		inval[scan] = scan
		retval[scan] = Conversion(scan,conv_type,sample_rate)
		conv1[scan] = retval[scan].conv1
		conv2[scan] = retval[scan].conv2
		conv3[scan] = retval[scan].conv3
		acc_out[scan] = retval[scan].acc_conv_a[0]
		
	print("Acc conversion: sample_freq=" + str(sample_rate))
	tmp = plt.subplot(1, 4, 1)
	plt.grid(color='0.95')
	plt.plot(inval, conv1, 'm', label="conv1")
	tmp.set_xlabel("conv1")
	tmp.set_ylabel("acc IU")
	plt.legend(title='Legend')
	tmp = plt.subplot(1, 4, 2)
	plt.grid(color='0.95')
	plt.plot(inval, conv2, 'g', label="conv2")
	tmp.set_xlabel("conv2")
	tmp.set_ylabel("acc IU")
	plt.legend(title='Legend')
	tmp = plt.subplot(1, 4, 3)
	plt.grid(color='0.95')
	plt.plot(inval, limit, color='gray', linestyle="dashed", label="limit")
	plt.plot(inval, conv3, 'y', label="conv3")
	tmp.set_xlabel("conv3")
	tmp.set_ylabel("acc IU")
	plt.legend(title='Legend')
	tmp = plt.subplot(1, 4, 4, title="Acc output")
	plt.grid(color='0.95')
	plt.plot(inval, acc_out, 'y', label="acc_out")
	tmp.set_xlabel("conv3")
	tmp.set_ylabel("acc IU")
	plt.legend(title='Legend')
	
	plt.show()

else:
	retval = Conversion(value,conv_type,PosLoop_Sample_Rate_H)
	print("Return value is: " + str(retval) + "\n");


