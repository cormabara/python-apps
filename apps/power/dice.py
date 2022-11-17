from enum import Enum,IntEnum


class Platforms(Enum):
    ALICONV = "ALICONV"
    ISDPRO = "ISDPRO"


class TimeUnity(float, Enum):
    S_to_S  = 1,
    S_to_nS = 1E9,
    S_to_10nS = 1E8,


def divshx(val_, shift_):
    return (int(val_) + (1 << (shift_ - 1))) >> shift_


def CheckIntOverflow(d_, numbits_):
    if abs(d_) > ((2 ** (numbits_-1)) - 1):
        # rpt_print("int32 overflow: " + str(d_))
        return True
    else:
        return False


class DConst:
    ALT_CPU_FREQ = 100000000
    SYSTMR_BASE_FREQ_HZ = 10000  # base frequency of the pwm
    CMP_RATE_BASE = int((ALT_CPU_FREQ / SYSTMR_BASE_FREQ_HZ) / 2)  # reference value for the compare

    ALICONV_CURR_FACTOR = 1536
    ISDPRO_CURR_FACTOR  = 12845
    ALICONV_MAX_CURRENT_A = 27
    ISDPRO_MAX_CURRENT_A = 250

    ALICONV_PWM_DEAD_TIME_S = 1.2E-6            # dead time for the igbt bridge
    ISDPRO_PWM_DEAD_TIME_S = 2E-6            # dead time for the igbt bridge


    PWM_HW_DELAY_S = 310E-9             # hw delay for the igbt bridge

    PWM_TICK_S = 10E-9            # Tick time for the pwm (10nS)

    def __init__(self):
        pass

    def mul_sqr_3(self,v_):
        return divshx(v_*1774,10)

    def PWM_TICK(self, unity_: TimeUnity):
        return self.PWM_TICK_S * unity_


    def PWM_HW_DELAY(self,unity_: TimeUnity):
        return self.PWM_HW_DELAY_S * unity_

class Dice:
    const_data: DConst

    def __init__(self, platform_, freq_shift_):
        self.platform = platform_
        self.const_data = DConst()
        self.freq_shift = freq_shift_
        self.pwm_frequency_hz = int(self.const_data.ALT_CPU_FREQ / self.const_data.SYSTMR_BASE_FREQ_HZ) >> self.freq_shift  # [hz]
        self.pwm_period_S = (1 / self.pwm_frequency_hz)  # periodo del pwm in uS
        self.pwm_max_duty = self.const_data.CMP_RATE_BASE << self.freq_shift
        self.PWM_DEAD_TIME_S = self.const_data.ALICONV_PWM_DEAD_TIME_S if self.platform == Platforms.ALICONV \
            else self.const_data.ISDPRO_PWM_DEAD_TIME_S
        print(type(self.const_data))

    @property
    def CData(self):
        return self.const_data

    def PwmPeriod(self, unity_: TimeUnity):
        return self.pwm_period_S*unity_

    def PWM_DEAD_TIME(self,unity_: TimeUnity = TimeUnity.S_to_S):
        return self.PWM_DEAD_TIME_S * unity_

class ThDice(Dice):

    class Current:
        def __init__(self, platform_):
            self.curr_factor = DConst.ALICONV_CURR_FACTOR if (platform_ == Platforms.ALICONV) \
                else DConst.ISDPRO_CURR_FACTOR
            self.max_current_A = DConst.ALICONV_MAX_CURRENT_A if (platform_ == Platforms.ALICONV) \
                else DConst.ISDPRO_MAX_CURRENT_A
            self.lsb2a_factor = self.curr_factor / (1024 * 1000)
            self.a2lsb_factor = (1024 * 1000) / self.curr_factor

        # Conversion current from lsb to A for the theorical calculation
        def Lsb2A(self, lsb_: float):
            return lsb_ * self.lsb2a_factor

        def A2lsb(self, A_: float):
            return A_ * self.a2lsb_factor

        @property
        def MaxCurrent_Lsb(self):
            return self.a2lsb_factor*self.max_current_A

    class CurrLoopV:

        def __init__(self):
            self.lsbph_factor = pow(2, 14)

        def Lsbph_2_Volt(self, vbus_, lsb_):
            return (vbus_ * lsb_) / self.lsbph_factor

        def Volt_2_Lsbph(self, vbus_, v_):
            return (v_ * self.lsbph_factor) / vbus_

    def __init__(self, platform_, freq_shift_):
        Dice.__init__(self, platform_, freq_shift_)
        self.current = self.Current(platform_)
        self.voltage = self.CurrLoopV()

    def Debug(self):
        tmpstr = "CONST AND VARS OF DICE\n"
        tmpstr += "Curr factor = " + str(self.current.curr_factor) + "\n"
        tmpstr += "Max current [A] = " + str(self.current.max_current_A) + "\n"
        tmpstr += "Max current [lsb] = " + str(self.current.MaxCurrent_Lsb) + "\n"
        return tmpstr

