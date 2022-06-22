# @file File with all conversion factor and conversion functions

from report import rpt_print


# fattore di conversione da lsb a mA (CURR_FACTOR/1024)
CURR_FACTOR = 12845

# Corrente massima
MAX_CURRENT_A = 200

# Fattore di conversione da lsm_ ad ampere
LSB2A_CURR_FACTOR = (CURR_FACTOR / (1024 * 1000))
A2LSB_CURR_FACTOR = (1024*1000) / CURR_FACTOR
MAX_CURRENT_LSB = MAX_CURRENT_A * A2LSB_CURR_FACTOR


# Conversion da Custom Watt a Watt
def Cu_2_W(val_cu):
	val_W = float(val_cu) / (1 << 16)
	return val_W


# Conversion da Watt a CustomWatt
def W_2_Cw(val_W):
	val_CW = val_W << 16
	return val_CW


def celsius_2_kelvin(val_):
	return val_ +  273,15


def kelvin_2_celsius(val_):
	return val_ -  273,15


def current_lsb_2_mA(lsb_):
	return (lsb_ * CURR_FACTOR) / 1024

def current_lsb_2_A(lsb_):
	return (lsb_ * CURR_FACTOR) / (1024 * 1000)


def current_lsb_2_A_get_error(lsb_):
	val1 = lsb_ * LSB2A_CURR_FACTOR
	val2 = ((current_lsb_2_mA(lsb_) * 131) / (1 << 17))
	val3 = (((lsb_ * CURR_FACTOR)/1024) * 131) / (1 << 17)
	val4 = (lsb_ * 131 * CURR_FACTOR) / ( (1 << 10) * ( 1 << 17) )
	val5 = (lsb_ * 131 * CURR_FACTOR) * (1 >> 27)
	# dove
	const_factor = float(131 * CURR_FACTOR) / float(0x8000000)		# 0.012537054717540741
	#rpt_print("current const factor = " + str(const_factor))

	if val1 == 0:
		# dbgprint("lsb_(" + str(lsb_) + ") val1 = 0")
		err_perc = 0
	else:
		err_perc = (val2 - val1) * 100 / val1;
		# dbgprint("lsb_(" + str(lsb_) + ") A(" + str(val1) + " - " + str(val2) +  ") lsb->a error(" + str(err) + ")\n")

	return err_perc


def iter_current_error():
	my_iter = range(int(MAX_CURRENT_LSB))
	low = -int(MAX_CURRENT_LSB)
	hi = int(MAX_CURRENT_LSB)
	data = [0 for i in my_iter]
	for index in my_iter:
		data[index] = current_lsb_2_A_get_error(low + index)

	maxerr_perc = max(data)
	# minerr_perc = min(data)

	rpt_print("for current lsb from " + str(low) + " to " + str(hi) + " the error is: " + str(maxerr_perc) + "[%]\n")