from enum import Enum

ALT_CPU_FREQ  = 100000000

SYSTMR_BASE_FREQ_HZ = 10000  # base frequency of the pwm

CMP_RATE_BASE = int( (ALT_CPU_FREQ/SYSTMR_BASE_FREQ_HZ)/2)  # reference value for the compare


DEAD_TIME = 2E-6            # dead time for the igbt bridge
HW_DELAY = 2E-6             # hw delay for the igbt bridge


PWM_TICK = 10E-8            # Tick time for the pwm (10nS)

class Ph2Ph(Enum):
    u_2_v = 1
    v_2_w = 2
    w_2_u = 3
