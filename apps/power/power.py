from constants import DEAD_TIME, HW_DELAY, PWM_TICK, CMP_RATE_BASE

'''
This is the main function for the power script

S = SQR(P^2 + Q^2)

P = V * I * cos(fi)
Q = V * I * sin(fi)
'''

FreqShift = 1  # shift of the base frequency da 100uS a 200uS shift = 1
pwm_max_duty = CMP_RATE_BASE << FreqShift
pwm_time = pwm_max_duty * PWM_TICK      # tempo totale di un colpo di PWM


def CalcTon(cmp_u_, cmp_v_, pwm_tick_):
    Ton = 2 * (abs(cmp_u_ - cmp_v_) * PWM_TICK) - (2 * DEAD_TIME) + (2 * HW_DELAY)
    return Ton


def CalcVphphOnePwm(Vbus_, ph_ph_, ton_):
    '''
    Funzione che calcola il valore della tensione fase fase su un giro di PWM
    '''
    VPh_2_Ph = (ton_ * Vbus_) / (2 * pwm_time)
    return VPh_2_Ph
