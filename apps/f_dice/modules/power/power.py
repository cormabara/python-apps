'''
This is the main module for the power script

Input data
    i_m_cmp2        =  0x660318  Motor_1->CL_CMPR_U      [NUM]      [0-10000]
    i_m_cmp1        =  0x660319  Motor_1->CL_CMPR_V      [NUM]      [0-10000]
    i_m_vbus_V      =  0x210104  Smps->Vbus_fbk_V        [V]        [0-1000]
    i_m_iurms_LSB   =  0x660322  Motor_1->CL_Iu_rms      [LSB]      [0-20000]
    i_m_vdref_LSB   =  0x660310  Motor_1->CL_Vd_ref      [LSB]      [0-14000]
    i_m_idfbk_LSB   =  0x66030E  Motor_1->CL_Vq_ref      [LSB]      [0-20000]
    i_m_vqref_LSB   =  0x66030D  Motor_1->CL_Id_fbk      [LSB]      [0-14000]
    i_m_iqfbk_LSB   =  0x66030B  Motor_1->CL_Iq_fbk      [LSB]      [0-20000]


S = SQR(P^2 + Q^2)

P = V * I * cos(fi)
Q = V * I * sin(fi)
'''
import math
import sys
from array import array

import math
from matplotlib import pyplot as plt
from enum import Enum, IntEnum
import numpy as np
import queue

from dice import ThDice, Platforms, TimeUnity, CheckIntOverflow
from mb_common_lib.report import rpt_print, rpt_sep, rpt_print_d

from f_dice.lib.my_timers import SysTimer
from f_dice.lib.tools import perc_err, divshx

FreqShift = 1  # shift of the base frequency da 100uS a 200uS shift = 1
glbl_dice = ThDice(Platforms.ALICONV, FreqShift)


class MyIIRFilter:
    _Fsample_Hz: float  # Cut frequency of the filter in Hz
    _Fcut_Hz: float  # Sample frequency in Hz
    _accumulator: float  # Accumulator for the filter

    _Wt: float  # Time constant of the filter

    def __init__(self, freq_sample_Hz_: float, freq_cut_Hz_: float):
        ''' Constructor of the filter with sample frequency and cut frequeny
        If cut frequency is 0 the filter is disabled '''
        self._Fsample_Hz = freq_sample_Hz_
        self._Fcut_Hz = freq_cut_Hz_
        self._Wt = (self._Fcut_Hz * 2 * math.pi * (pow(2, 16))) / self._Fsample_Hz
        self._accumulator = 0

    # Reset the accumulator of the filter
    def Reset(self):
        self._accumulator = 0

    # Add a sample to filter and return the filtered value
    def Sample(self, sample_):
        if self._Fcut_Hz != 0:
            err = sample_ - self._accumulator / pow(2, 16)
            self._accumulator = self._accumulator + (err * self._Wt)
            return self._accumulator / pow(2, 16)
        else:
            return sample_

    # Get the value of the filter
    def GetVal(self):
        val = self._accumulator / pow(2, 16)


# This function take a fload, evaluate the rounding error to int, check the overflow and return
# the integer
def check_value(value_float_: float, print_):
    overflow = False
    if print_:
        if int(value_float_) != 0:
            err = perc_err(value_float_, int(value_float_))
        else:
            err = 0
        overflow = CheckIntOverflow(value_float_, 32)
        rpt_print("Op: err%(" + str(err) + ") overflow(" + str(overflow) + ")")

    if overflow == True:
        sys.exit(-2);

    return int(value_float_)


class InMData(IntEnum):
    i_m_cmp1 = 0,
    i_m_cmp2 = 1,
    i_m_vbus_V = 2,
    i_m_iurms_LSB = 3,
    i_m_vdref_LSB = 4,
    i_m_idfbk_LSB = 5,
    i_m_vqref_LSB = 6,
    i_m_iqfbk_LSB = 7,
    i_m_datas = 8,

class PowerSMData(IntEnum):
    i_m_cmp1 = 0,
    i_m_cmp2 = 1,
    i_m_vbus_V = 2,
    i_m_iurms_LSB = 3,
    i_m_PowerS_voltlsb = 4,
    i_m_PowerS_W = 5,
    i_m_cosphi = 6,
    i_m_datas = 7,

class PowerPMData(IntEnum):
    i_m_vdref_LSB = 0,
    i_m_idfbk_LSB = 1,
    i_m_vqref_LSB = 2,
    i_m_iqfbk_LSB = 3,
    i_m_PowerP_lsblsb = 4,
    i_m_PowerP_W = 5,
    i_m_cosphi = 6,
    i_m_datas = 7,


class OutMDataTheo(IntEnum):
    o_m_ton_S = 0
    o_m_ton_10nS = 1
    o_m_vph_V = 2
    o_m_vphrms_V = 3
    o_m_powerS_VA = 4
    o_m_powerP_W = 5
    o_m_datas = 6


class OutMDataReal(IntEnum):
    o_m_ton_10nS = 0
    o_m_ton_half_10nS = 1
    o_m_vphrms_V = 2
    o_m_powerS_voltlsb = 3
    o_m_powerP_lsblsb = 4
    o_m_powerS_VA = 5
    o_m_powerP_W = 6
    o_m_datas = 7

class MidMData(IntEnum):
    p_m_iurms_A = 0,
    p_m_vdref_V = 1,
    p_m_idfbk_A = 2,
    p_m_vqref_V = 3,
    p_m_iqfbk_A = 4,
    p_m_datas = 5,


class PowerSample:


    def __init__(self, in_row_):
        self.debugprint = False
        self.inRow = in_row_
        elements = int(MidMData.p_m_datas)

        self.midRow = np.zeros(elements)
        self.outRowTheo = np.zeros(OutMDataTheo.o_m_datas)
        self.outRowReal = np.zeros(OutMDataReal.o_m_datas)

    def DbgPrint(self,dbgstr: str):
        if self.debugprint:
            rpt_print(dbgstr)

    def DbgPrintD(self,dbgstr: str,val_:float):
        if self.debugprint:
            rpt_print_d(dbgstr,val_)

    def DbgPrintSep(self):
        if self.debugprint:
            rpt_sep()

    def Check_Theo_Real(self):
        rpt_sep()
        self.DbgPrint("CHECK THEO / REAL CALCULATION")


        theo = self.outRowTheo[OutMDataTheo.o_m_vphrms_V]
        real = self.outRowReal[OutMDataReal.o_m_vphrms_V]
        real_2_theo = self.outRowReal[OutMDataReal.o_m_vphrms_V]
        err = theo - real_2_theo
        self.DbgPrint("v ph rms: theo(" + str(theo) +
                    ") real("+ str(real_2_theo) +
                    ") error(" + str(err) + ") error_perc(" + str((err*100)/theo) +")")

        theo = self.outRowTheo[OutMDataTheo.o_m_powerS_VA]
        real = self.outRowReal[OutMDataReal.o_m_powerS_voltlsb]
        real_2_theo = int(self.outRowReal[OutMDataReal.o_m_powerS_VA])
        err = theo - real_2_theo
        self.DbgPrint("Power S: theo(" + str(theo) +
                    ") real("+ str(real_2_theo) +
                    ") error(" + str(err) + ") error_perc(" + str((err*100)/theo) +")")

        theo = self.outRowTheo[OutMDataTheo.o_m_powerP_W]
        real = self.outRowReal[OutMDataReal.o_m_powerP_lsblsb]
        real_2_theo = self.outRowReal[OutMDataReal.o_m_powerP_W]
        err = theo - real_2_theo
        self.DbgPrint("Power P: theo(" + str(theo) +
                    ") real("+ str(real_2_theo) +
                    ") error(" + str(err) + ") error_perc(" + str((err*100)/theo) +")")

    def PrintData(self):
        if self.debugprint:
            rpt_print(glbl_dice.Debug())
            rpt_print("pwm_period [S]: " + str(glbl_dice.pwm_period_S))
            rpt_print("PWM_TICK [S]: " + str(glbl_dice.CData.PWM_TICK_S))
            rpt_sep()
            rpt_print("InData:\n " + str(self.inRow[np.newaxis].T))
            rpt_sep()
            rpt_print("MidData:\n " + str(self.midRow[np.newaxis].T))
            rpt_sep()
            rpt_print("OutData Theo:\n " + str(self.outRowTheo[np.newaxis].T))
            rpt_sep()
            rpt_print("OutData Real:\n " + str(self.outRowReal[np.newaxis].T))


class PowerSampleS(PowerSample):

    def __init__(self, inrow_):
        PowerSample.__init__(self, inrow_)
        self.midRow[MidMData.p_m_iurms_A] = glbl_dice.current.Lsb2A(self.inRow[InMData.i_m_iurms_LSB])

    def _CalcTon_S(self):
        '''
        Funzione che calcola il tempo Ton in cui abbiamo applicato la tensione Vbus sulla fase
        '''
        cmp_diff = abs(self.inRow[InMData.i_m_cmp1] - self.inRow[InMData.i_m_cmp2])
        self.DbgPrint("compare diff(" + str(cmp_diff) + ")")
        pwmtick = glbl_dice.CData.PWM_TICK_S
        self.DbgPrint("pwmtick(" + str(pwmtick) + ")")
        pwmdt = glbl_dice.PWM_DEAD_TIME()
        self.DbgPrint("pwmdt(" + str(pwmdt) + ")")
        # pwmhwdel = glbl_dice.CData.PWM_HW_DELAY_S
        # self.DbgPrint("pwmhwdel(" + str(pwmhwdel) + ")")
        pwmhwdel = 0
        ton_S = 2 * (abs(cmp_diff) * pwmtick) - (2 * pwmdt) + (2 * pwmhwdel)
        if ton_S < 0:
            ton_S = 0

        self.DbgPrintD("Ton [S]", ton_S)
        self.outRowTheo[OutMDataTheo.o_m_ton_S] = ton_S
        self.outRowTheo[OutMDataTheo.o_m_ton_10nS] = ton_S * 1E8

    def _CalcHalfTon_10nS(self):
        '''
        Funzione che calcola il tempo Ton/2 in cui abbiamo applicato la tensione Vbus sulla fase
        '''
        cmp_diff = int(abs(self.inRow[InMData.i_m_cmp1] - self.inRow[InMData.i_m_cmp2]))
        self.DbgPrint("compare diff(" + str(cmp_diff) + ")")
        pwmtick = int(glbl_dice.CData.PWM_TICK(TimeUnity.S_to_10nS))
        self.DbgPrint("pwmtick(" + str(pwmtick) + ")")
        pwmdt = int(glbl_dice.PWM_DEAD_TIME(TimeUnity.S_to_10nS))
        self.DbgPrint("pwmdt(" + str(pwmdt) + ")")
        # pwmhwdel = int(glbl_dice.CData.PWM_HW_DELAY(TimeUnity.S_to_10nS))
        # self.DbgPrint("pwmhwdel(" + str(pwmhwdel) + ")")
        pwmhwdel = 0

        ton_10nS = 2 * (abs(cmp_diff) * pwmtick) - (2 * pwmdt) + (2 * pwmhwdel)
        if ton_10nS < 0:
            ton_10nS = 0
        self.outRowReal[OutMDataReal.o_m_ton_10nS] = int(ton_10nS)
        self.DbgPrint("Ton [10nS]: " + str(ton_10nS))
        ton_half_10nS = ton_10nS/2
        self.DbgPrint("Ton half [10nS]: " + str(ton_half_10nS))
        self.outRowReal[OutMDataReal.o_m_ton_half_10nS] = int(ton_half_10nS)

    def _Calc_VPhase_Theo_V(self, iir_filter_: MyIIRFilter):
        ton = self.outRowTheo[OutMDataTheo.o_m_ton_S]
        vbus = self.inRow[InMData.i_m_vbus_V]
        vph = (ton * pow(vbus, 2)) / glbl_dice.pwm_period_S
        self.outRowTheo[OutMDataTheo.o_m_vph_V] = vph
        val = iir_filter_.Sample(vph)
        self.outRowTheo[OutMDataTheo.o_m_vphrms_V] = math.sqrt(val)

    def _Calc_VPhase_Real_V(self, iir_filter_: MyIIRFilter):
        ton_half_10nS = self.outRowReal[OutMDataReal.o_m_ton_half_10nS]
        pwmperiod_half_10nS = int(glbl_dice.PwmPeriod(TimeUnity.S_to_10nS)/2)
        self.DbgPrintD("pwmperiod [10nS]", pwmperiod_half_10nS)

        vbus_V = self.inRow[InMData.i_m_vbus_V]
        vph_V = int(ton_half_10nS * pow(vbus_V, 2) / pwmperiod_half_10nS)
        self.DbgPrintD("v ph^2 [V]", vph_V)
        val = int(iir_filter_.Sample(vph_V))
        self.DbgPrintD("v ph^2 rms[V]", val)
        val = int(math.sqrt(val))
        self.DbgPrintD("v ph rms[V]", val)
        # val = glbl_dice.voltage.Volt_2_Lsbph(self.inRow[InMData.i_m_vbus_V], val)
        self.outRowReal[OutMDataReal.o_m_vphrms_V] = val
        self.DbgPrintD("v ph rms[V]", self.outRowReal[OutMDataReal.o_m_vphrms_V])

    def _CalcPowerS_Theo_VA(self):
        '''
        Calcolo della potenza apparente usando la corrente e la tensione rms di una singola fase (calcolata in [VA]
        '''
        self.outRowTheo[OutMDataTheo.o_m_powerS_VA] = math.sqrt(3) * self.outRowTheo[OutMDataTheo.o_m_vphrms_V] * self.midRow[MidMData.p_m_iurms_A]

    def _CalcPowerS_Real_voltlsb(self):
        '''
        Calcolo della potenza apparente [volt*lsb]usando la corrente e la tensione rms di una singola fase (calcolata in [VA]
        '''
        prd = int(self.outRowReal[OutMDataReal.o_m_vphrms_V]) * int(self.inRow[InMData.i_m_iurms_LSB])
        powSlsb = int(glbl_dice.CData.mul_sqr_3(prd))
        self.DbgPrint("Power S [volt-lsb]: " + str(powSlsb))
        self.outRowReal[OutMDataReal.o_m_powerS_voltlsb] = int(powSlsb)

    def _CalcPowerS_Real_VA(self):
        '''
        Calcolo della potenza apparente[Watt]
        '''
        powSlsb = self.outRowReal[OutMDataReal.o_m_powerS_voltlsb]
        powSva = int(glbl_dice.current.Lsb2A(powSlsb))
        self.DbgPrint("Power S [VA]: " + str(powSva))
        self.outRowReal[OutMDataReal.o_m_powerS_VA] = int(powSva)

    def _PowS_Lsblsb_to_VA(self, powIn_):
        pow_temp = powIn_
        pow_temp = pow_temp / 2^14
        # pow_temp *= glbl_dice.CData.
        pow_temp >>= 8;
        # Pow_lsb * curr_factor / 1000  ->    mul(131)  sh(17)   err % (0.05493164062500208)
        pow_temp = divshx((pow_temp * 131), 5);
        return pow_temp

    def _CalcPowerS_Theo(self,iir_filter_: MyIIRFilter):
        self._CalcTon_S()
        self._Calc_VPhase_Theo_V(iir_filter_)
        self._CalcPowerS_Theo_VA()

    def _CalcPowerS_Real(self,iir_filter_: MyIIRFilter):
        self._CalcHalfTon_10nS()
        self._Calc_VPhase_Real_V(iir_filter_)
        self._CalcPowerS_Real_voltlsb()
        self._CalcPowerS_Real_VA()

    def CalcPower(self, iir_filter_: MyIIRFilter):
        self._CalcPowerS_Theo(iir_filter_)
        self._CalcPowerS_Real(iir_filter_)


class PowerSampleP(PowerSample):

    def __init__(self,in_row_):
        PowerSample.__init__(self, in_row_)
        self.midRow[MidMData.p_m_idfbk_A] = glbl_dice.current.Lsb2A(self.inRow[InMData.i_m_idfbk_LSB])
        self.midRow[MidMData.p_m_iqfbk_A] = glbl_dice.current.Lsb2A(self.inRow[InMData.i_m_iqfbk_LSB])
        self.midRow[MidMData.p_m_vdref_V] = glbl_dice.voltage.Lsbph_2_Volt(self.inRow[InMData.i_m_vbus_V], self.inRow[InMData.i_m_vdref_LSB])
        self.midRow[MidMData.p_m_vqref_V] = glbl_dice.voltage.Lsbph_2_Volt(self.inRow[InMData.i_m_vbus_V], self.inRow[InMData.i_m_vqref_LSB])

    def _CalcPowerP_Theo_W(self):
        '''
        Calcolo della potenza attiva usando la tensione applicata dall'anello di corrente per la corrente riletta dallo stesso anello
        '''
        wq = self.midRow[MidMData.p_m_vqref_V] * self.midRow[MidMData.p_m_iqfbk_A]
        wd = self.midRow[MidMData.p_m_vdref_V] * self.midRow[MidMData.p_m_idfbk_A]
        self.outRowTheo[OutMDataTheo.o_m_powerP_W] = wq + wd

    def _CalcPowerP_Real_lsblsb(self):
        '''
        Calcolo della potenza attiva usando la tensione applicata dall'anello di corrente per la corrente riletta dallo stesso anello
        '''
        wq_lsblsb = int(self.inRow[InMData.i_m_vqref_LSB] * self.inRow[InMData.i_m_iqfbk_LSB])
        wd_lsblsb = int(self.inRow[InMData.i_m_vdref_LSB] * self.inRow[InMData.i_m_idfbk_LSB])
        powPlsb = wq_lsblsb + wd_lsblsb
        check_value(powPlsb, self.debugprint)
        self.outRowReal[OutMDataReal.o_m_powerP_lsblsb] = powPlsb
        self.DbgPrint("Power P [lsb]: " + str(powPlsb))

    def _CalcPowerP_Real_W(self):
        '''
        COnversione della potenza da lsb * lsb in watt, attenzione overflow
        '''
        powPlsb = self.outRowReal[OutMDataReal.o_m_powerP_lsblsb]
        powPw = int(glbl_dice.current.Lsb2A(glbl_dice.voltage.Lsbph_2_Volt(self.inRow[InMData.i_m_vbus_V], powPlsb)))
        self.DbgPrint("Power P [W]: " + str(powPw))
        self.outRowReal[OutMDataReal.o_m_powerP_W] = powPw

    def _CalcPowerP_Theo(self):
        self._CalcPowerP_Theo_W()

    def _CalcPowerP_Real(self):
        self._CalcPowerP_Real_lsblsb()
        self._CalcPowerP_Real_W()

    def CalcPower(self):
        self._CalcPowerP_Theo()
        self._CalcPowerP_Real()


class PowerType(IntEnum):
    pow_S = 0,
    pow_P = 1,


class PowerData:

    FREQ_SAMPLE = 1 / 200e-6  # [s] Sampling
    FREQ_CUT = 0 #5  # [Hz]

    def __init__(self):
        self.iir_filter = None

        self.size = 0
        self.irq_queue = queue.Queue()
        self.main_counter = 0
        self.irq_queueS = queue.Queue()
        self.irq_queueP = queue.Queue()
        self.samplesCount = any
        self.SamplesS: PowerSampleS = []
        self.SamplesP: PowerSampleP = []
        self.SetFilter(self.FREQ_SAMPLE,self.FREQ_CUT)

    def SetFilter(self, fsample_, fcut_):
        self.iir_filter = MyIIRFilter(fsample_, fcut_)

    def InitFromData(self, indata: np.array ):
        self.size = len(indata)
        sample_iter = range(int(self.size))
        self.InData = indata
        self.SamplesS = [PowerSampleS(indata[i]) for i in sample_iter]
        self.SamplesP = [PowerSampleP(indata[i]) for i in sample_iter]
        self.samplesCount = [ite for ite in sample_iter]

    def GetVector(self, pt_: PowerType):
        return self.SamplesS if pt_ is PowerType.pow_S else self.SamplesP


    def GetInData(self):
        return self.InData
        # pos = 0
        # output = np.zeros((self.size, InMData.i_m_datas))
        # for sample in self.Samples:
        #     output[pos] = sample.inRow
        #     pos += 1
        # return output

    def GetMidData(self, pt_: PowerType):
        pos = 0
        output = np.zeros((self.size, MidMData.p_m_datas))
        for sample in self.GetVector(pt_):
            output[pos] = sample.midRow
            pos += 1
        return output

    def GetOutReal(self, pt_: PowerType):
        pos = 0
        output = np.zeros((self.size, OutMDataReal.o_m_datas))
        for sample in self.GetVector(pt_):
            output[pos] = sample.outRowReal
            pos += 1
        return output

    def GetOutTheo(self, pt_: PowerType):
        pos = 0
        output = np.zeros((self.size, OutMDataTheo.o_m_datas))
        for sample in self.GetVector(pt_):
            output[pos] = sample.outRowTheo
            pos += 1
        return output

    def irq_simulation(self, row_):
        '''
        Simulazione della routine sotto irq che esegue un campionamento completo della grandezze in ingresso
        '''
        self.irq_queueS.put(PowerSampleS(row_))
        self.irq_queueP.put(PowerSampleP(row_))

    def AddSample(self, index_, pt_: PowerType, sample: PowerSample):
        self.GetVector(pt_)[index_] = sample

    def main_simulation(self):
        '''
        Simulazione della routine sotto main che esegue i calcoli
        '''
        end = False
        while end is False:
            try:
                cnt = self.irq_queue.qsize()
                sampleS: PowerSampleS = self.irq_queueS.get(False, 0)
                sampleP: PowerSampleP = self.irq_queueP.get(False, 0)
                # rpt_print("Get sample: main_counter:(" + str(self.main_counter) + ") queue_size:(" + str(cnt) + ")")
                sampleS.CalcPower(self.iir_filter)
                sampleP.CalcPower()
                self.AddSample(self.main_counter, PowerType.pow_S, sampleS)
                self.AddSample(self.main_counter, PowerType.pow_P, sampleP)
                self.main_counter += 1
            except queue.Empty:
                end = True

    def GraphPowers(self):
        '''
        Stampa grafico delle potenze theo e real 
        '''
        dinput = self.GetInData().T

        pt = PowerType.pow_S
        dmiddata_s = self.GetMidData(pt).T
        theo_s = self.GetOutTheo(pt).T
        real_s = self.GetOutReal(pt).T

        pt = PowerType.pow_P
        dmiddata_p = self.GetMidData(pt).T
        theo_p = self.GetOutTheo(pt).T
        real_p = self.GetOutReal(pt).T

        plt.subplot(2, 3, 1, title="T_on")
        plt.grid(color='0.95')
        plt.plot(self.samplesCount, real_s[OutMDataReal.o_m_ton_10nS], 'm', label="S real")
        plt.plot(self.samplesCount, theo_s[OutMDataTheo.o_m_ton_10nS], 'b', label="S theo")
        plt.legend(title='Legend')
        plt.subplot(2, 3, 2, title="Vph rms")
        plt.grid(color='0.95')
        plt.plot(self.samplesCount, real_s[OutMDataReal.o_m_vphrms_V], 'm', label="S real")
        plt.plot(self.samplesCount, theo_s[OutMDataTheo.o_m_vphrms_V], 'b', label="S theo")
        plt.legend(title='Legend')
        plt.subplot(2, 3, 3, title="Debug Real")
        plt.grid(color='0.95')
        # plt.plot(self.samplesCount, theo_s[OutMDataReal.o_m_ton_10nS], 'm', label="Ton_10nS")
        plt.plot(self.samplesCount, dmiddata_s[MidMData.p_m_iurms_A], 'g', label="Iu rms A")
        # plt.plot(self.samplesCount, theo_s[OutMDataTheo.o_m_vphrms_V], 'b', label="S volt/ampere")
        # plt.plot(self.samplesCount, theo_s[OutMDataTheo.o_m_powerS_VA], 'b', label="S volt/ampere")
        plt.legend(title='Legend')

        plt.subplot(2, 3, 4, title="POWER P")
        plt.grid(color='0.95')
        plt.plot(self.samplesCount, real_p[OutMDataReal.o_m_powerP_W], 'm', label="P real")
        plt.plot(self.samplesCount, theo_p[OutMDataTheo.o_m_powerP_W], 'b', label="P theo")
        plt.legend(title='Legend')
        plt.subplot(2, 3, 5, title="POWER S")
        plt.grid(color='0.95')
        plt.plot(self.samplesCount, real_s[OutMDataReal.o_m_powerS_VA], 'm', label="S real")
        plt.plot(self.samplesCount, theo_s[OutMDataTheo.o_m_powerS_VA], 'b', label="S theo")
        plt.legend(title='Legend')
        plt.show()

    def Means(self):
        dinput = self.GetInData().T

        pt = PowerType.pow_S
        dmiddata_s = self.GetMidData(pt).T
        theo_s = self.GetOutTheo(pt).T
        real_s = self.GetOutReal(pt).T

        pt = PowerType.pow_P
        theo_p = self.GetOutTheo(pt).T
        real_p = self.GetOutReal(pt).T

        iu_rms_lsb_mean = np.mean(dinput[InMData.i_m_iurms_LSB])
        rpt_print("Iu rms [lsb] mean value: Input(" + str(iu_rms_lsb_mean) + ")")
        half_ton_r = np.mean(real_s[OutMDataReal.o_m_ton_half_10nS])
        rpt_print("Half Ton[10nS] mean value: Real(" + str(half_ton_r) + ")")

        vph_mean_t = np.mean(theo_s[OutMDataTheo.o_m_vphrms_V])
        vph_mean_r = np.mean(real_s[OutMDataReal.o_m_vphrms_V])
        rpt_print("Vphph rms [V] mean value: Real(" + str(vph_mean_r) + ") Theo(" + str(vph_mean_t) + ")")

        psvlsb_mean_r = np.mean(real_s[OutMDataReal.o_m_powerS_voltlsb])
        rpt_print("PowerS [V*lsb] mean value: Real(" + str(psvlsb_mean_r) + ")")

        ps_mean_t = np.mean(theo_s[OutMDataTheo.o_m_powerS_VA])
        ps_mean_r = np.mean(real_s[OutMDataReal.o_m_powerS_VA])
        rpt_print("PowerS [VA] mean value: Real(" + str(ps_mean_r) + ") Theo(" + str(ps_mean_t) + ")")

        pp_mean_t = np.mean(theo_p[OutMDataTheo.o_m_powerP_W])
        pp_mean_r = np.mean(real_p[OutMDataReal.o_m_powerP_W])
        rpt_print("PowerP [W] mean value: Real(" + str(pp_mean_r) + ") Theo(" + str(pp_mean_t) + ")")


def CalculateSingle(row_):

    powerData = PowerData()
    powerData.SetFilter(powerData.FREQ_SAMPLE, 0)

    sampleS = PowerSampleS(row_)
    sampleS.CalcPower(powerData.iir_filter)
    sampleS.PrintData()
    sampleS.Check_Theo_Real()

    sampleP = PowerSampleP(row_)
    sampleP.CalcPower()
    sampleP.PrintData()
    sampleP.Check_Theo_Real()
    pass


def Simulate(data):

    powerData = PowerData()
    irq_timer = SysTimer(0)
    main_timer = SysTimer(0)
    size = len(data)
    powerData.InitFromData(data)
    row = 0
    finish_loop = 0

    try:
        while finish_loop < 2:
            if irq_timer.CheckLoop() is True:
                if row < size:
                    powerData.irq_simulation(data[row])
                    row = row + 1
                else:
                    finish_loop = 1

            if finish_loop < 2 and main_timer.CheckLoop() is True:
                if not powerData.main_simulation():
                    if finish_loop == 1:
                        finish_loop = 2

        rpt_print("end loop")

    except KeyboardInterrupt:
        print('interrupted!')

    return powerData

def CalculateCsv():
    pass
