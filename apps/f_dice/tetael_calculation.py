# Calculation of the teta_el starting from teta_mc

import numpy as np
import matplotlib.pyplot as plt
from mb_common_lib import types


TURNS_COUNT = 4096
TETA_NBITS = 10
NUM_POLES = 7

def WRAP_MASK_RE(bs_):	
	return U32((1<<(bs_))-1)
def WRAP_MASK_TH(bs_):	
	return (1<<(bs_))-1


def TETA_WRAP_TH(angle_):
	return ((angle_) & WRAP_MASK_TH(TETA_NBITS))
def TETA_WRAP_RE(angle_):
	return ((angle_) & WRAP_MASK_RE(TETA_NBITS))

tetamc = [i for i in range(1,TURNS_COUNT)]
tetael_th = [0 for i in range(1,TURNS_COUNT)]
tetael_re = [0 for i in range(1,TURNS_COUNT)]
round_error = [0 for i in range(1,TURNS_COUNT)]

for iter in range(0,TURNS_COUNT-1):
	tetael_re[iter] = int((iter * int(NUM_POLES << TETA_NBITS))/TURNS_COUNT)
	tetael_th[iter] = (iter * (NUM_POLES << TETA_NBITS))/TURNS_COUNT
	round_error[iter] = tetael_th[iter] - tetael_re[iter]


print("Teta mc calcultion")
tmp = plt.subplot(1, 1, 1)
plt.grid(color='0.95')
plt.plot(tetamc, round_error, 'm', label="teta_el")
tmp.set_xlabel("teta_mc")
tmp.set_ylabel("teta_el")
plt.legend(title='Legend')
plt.show()
