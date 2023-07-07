import math
from f_dice.lib.tools import divshx
from f_dice.lib.tools import CheckIntOverflow
import matplotlib.pyplot as plt


def errorOnOverflow32(d_):
	if CheckIntOverflow(d_, 32):
		print("error overlow")
		return True
	return False


def MyPlot(r_, c_, i_, title_, x_, y_):
	ptmp = plt.subplot(r_, c_, i_)
	plt.title = title_
	plt.grid(color='0.95')
	plt.plot(x_, y_, 'm', label=title_)
	ptmp.set_xlabel("x")
	ptmp.set_ylabel("y")
	plt.legend(title=title_)


VBUS_FBK_V = 600
MAX_FREQUENCY = 70
OMEGA = MAX_FREQUENCY * 2 * math.pi
M_Lm_uH = 5000
Iq_ref_mA = 254558
#Iq_ref_mA = 10
omega_l = OMEGA * M_Lm_uH  # [rad/s * uH]

if VBUS_FBK_V:
	currRange = range(0, Iq_ref_mA)
	input = [i for i in currRange]
	data1 = [[0 for i in currRange] for j in range(2)]
	I_ref_A_lsh3 = [0 for i in currRange]
	data2 = [[0 for i in currRange] for j in range(4)]

	buffer1 = [0 for i in currRange]
	buffer2 = [0 for i in currRange]

	CL_decoupling_V = [0 for i in currRange]
	CL_decoupling_lsb = [0 for i in currRange]


	print("starting loop")
	for current in currRange:
		# calcolo di Vd_decoupling, dipendente dalla Iq_fbk (ma si usa la Iq_ref perche' la Iq_ref e' piu' rapida a crescere)
		temp = data1[0][current] = current * 131
		if errorOnOverflow32(temp):
			print("data1_0:" + str(temp))
		temp = data1[1][current] = int(temp) >> 14
		if errorOnOverflow32(temp):
			print("data1_1:" + str(temp))

		I_ref_A_lsh3[current] = divshx(current * 131, 14)		# ((I_fbk[mA] * 131) >> 14) = (I_fbk[A] << 3)
		# mul (67)	 sh (26)	 err% (0.162220001221)

		temp = data2[0][current] = omega_l * 67
		if errorOnOverflow32(temp):
			print("data2_0:" + str(temp))

		temp = data2[1][current] = int(temp) >> 8
		if errorOnOverflow32(temp):
			print("data2_1:" + str(temp))

		buffer1[current] = divshx((omega_l * 67),8)
		buffer2[current] = divshx((buffer1[current] * I_ref_A_lsh3[current]), 18+3)
		CL_decoupling_V[current] = divshx((omega_l * 67 * I_ref_A_lsh3[current]), 26+3)

		temp = data2[2][current] = temp * I_ref_A_lsh3[current]
		if errorOnOverflow32(temp):
			print("data2_2:" + str(temp))

		temp = data2[3][current] = temp >> 18+3
		if errorOnOverflow32(temp):
			print("data2_3:" + str(temp))

		CL_decoupling_lsb[current] = voltage_V2DriveIu(CL_decoupling_V[current], VBUS_FBK_V)

	temp = data1[0]
	MyPlot(4, 2, 1, "data1_0", input, data1[0])
	MyPlot(4, 2, 2, "data1_1", input, data1[1])
	MyPlot(4, 2, 3, "data2_0", input, data2[0])
	MyPlot(4, 2, 4, "data2_1", input, data2[1])
	MyPlot(4, 2, 5, "data2_2", input, data2[2])
	MyPlot(4, 2, 6, "data2_3", input, data2[3])
	MyPlot(4, 2, 7, "Vd_Vq", input, CL_decoupling_lsb)
	plt.show()

	MyPlot(3, 2, 1, "I_ref_A_lsh3", input, I_ref_A_lsh3)
	MyPlot(3, 2, 2, "buffer1", input, buffer1)
	MyPlot(3, 2, 3, "buffer2", input, buffer2)
	MyPlot(3, 2, 4, "CL_decoupling_V", input, CL_decoupling_V)
	MyPlot(3, 2, 5, "Vd_Vq", input, CL_decoupling_lsb)
	plt.show()