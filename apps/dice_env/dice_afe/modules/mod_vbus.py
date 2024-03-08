"""" Mdule for the VBUS handling: most of all is the VBUS_PID """
from collections import deque

from afe_config import AfeSignals, CnfAfe
from my_pid import MyPid
from my_types import S32_MAX
from range_limits import check_out_range
from report import MyReport
from tools import divshxu, divshx

VBUS_LSB_2_V_MUL = 352  # Moltiplicatore VBus per conversione lsb->V
VBUS_LSB_2_V_SHIFT = 13  # Shift VBus per conversione lsb->V
VBUS_V_2_LSB_MUL = 5954  # Moltiplicatore VBus per conversione V->lsb
VBUS_V_2_LSB_SHIFT = 8  # Shift VBus per conversione V->lsb
VBUS_NON_LINEARITY_MUL = 1  # Mul factor for non linearity compensation
VBUS_NON_LINEARITY_SHIFT = 0  # Div factor for non linearity compensation


def MainVbus_V2lsb(valv_):
    return divshxu(valv_ * VBUS_V_2_LSB_MUL, VBUS_V_2_LSB_SHIFT)


def MainVbus_lsb2V(vallsb_):
    return divshxu(vallsb_ * VBUS_LSB_2_V_MUL, VBUS_LSB_2_V_SHIFT)


class VBusPid:

    def __init__(self, rm_):
        self.ref_ramp_lsb_s = 0
        self.ramp_lsb_s = 0
        self.effort = 0
        self.step_irq = 0
        self.target_volt = 0
        self.target_lsb = 0
        self.step_tick_timeout = 0
        self.step_tick_counter = 0
        self.reference_lsb = 0
        self.reference_volt = 0
        self.ramp_volt_sec = 0
        self.pid = MyPid(rm_)

    def init(self):
        self.pid.kp = CnfAfe().dict_get_par("vbus_pid_kp")
        self.pid.ki = CnfAfe().dict_get_par("vbus_pid_ki")
        self.pid.shift_kp = CnfAfe().dict_get_par("vbus_pid_shift_kp")
        self.pid.shift_ki = CnfAfe().dict_get_par("vbus_pid_shift_ki")
        self.target_volt = CnfAfe().dict_get_par("vbus_pid_ref_target_V")
        self.ramp_volt_sec = CnfAfe().dict_get_par("vbus_pid_ref_ramp_V_s")

        self.target_lsb = MainVbus_V2lsb(self.target_volt)
        self.ref_ramp_lsb_s = MainVbus_V2lsb(self.ramp_volt_sec)

        if not self.ref_ramp_lsb_s:
            self.ref_ramp_lsb_s = 1

        # self.step_irq = (self.ramp_lsb_s / CnfAfe().SYSTMR_FREQ_HZ) ? (vbuspid_->ref_ramp_lsb_s / SYSTMR_FREQ_HZ): 1;
        if self.ramp_lsb_s / CnfAfe().SYSTMR_FREQ_HZ:
            self.step_irq = self.ref_ramp_lsb_s / CnfAfe().SYSTMR_FREQ_HZ
        else:
            self.step_irq = 1

        self.step_tick_timeout = CnfAfe().SYSTMR_FREQ_HZ / self.ref_ramp_lsb_s
        self.pid.reset()

    def _calculate_reference(self,vbus_fbk_lsb_,go_target_):
        delta = self.target_lsb - self.reference_lsb
        self.step_tick_counter -= 1

        if not go_target_:
            self.reference_lsb = vbus_fbk_lsb_
            self.step_tick_counter = self.step_tick_timeout
        elif delta and self.step_tick_counter <= 0:
            if delta > 0:
                self.reference_lsb += delta if delta < self.step_irq else self.step_irq
            else:
                self.reference_lsb += delta if delta > -self.step_irq else - self.step_irq

        self.step_tick_counter = self.step_tick_timeout

        return self.reference_lsb

    def calculate_effort(self,vbus_fbk_lsb_, go_target_):
        reference = self._calculate_reference(vbus_fbk_lsb_, go_target_)
        self.effort = self.pid.output( vbus_fbk_lsb_ - reference)


class ModVBus:

    VBUS_MAX_STABLE = S32_MAX

    def VBUS_MIN_STABLE(self,vac_):
        return divshx(vac_ * 85, 8)

    def __init__(self,rm_):
        self.vbus_fbk_lsb = None        # @todo Questo viene dall'uscita del bridge
        self.vbus_fbk_v = 0
        self.rm = rm_
        self.go_target = False
        self.vbus_pid = VBusPid(rm_)
        # Queue for the plot
        self.plt_target_lsb = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.plt_reference_lsb = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.plt_target_volt = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)
        self.plt_reference_volt = deque([i for i in CnfAfe().display_range()], maxlen=CnfAfe().WIN_DEEP)

    def init(self):
        self.vbus_pid.init()
        pass

    def start(self):
        pass


    def read_vbus(self):
        self.vbus_fbk_lsb = AfeSignals().Fpga_Vbus_fbk_lsb
        self.vbus_fbk_v = MainVbus_lsb2V(self.vbus_fbk_lsb)

    def check_vbus_stable(self, vac_):
        return check_out_range(self.vbus_fbk_v, self.VBUS_MIN_STABLE(vac_), self.VBUS_MAX_STABLE)

    def handle(self):
        self.read_vbus()
        self.vbus_pid.calculate_effort(self.vbus_fbk_lsb,self.go_target)
        self.plot_sample()
        pass

    def background(self):
        pass

    def plot_sample(self):
        """ Aggiorno i vettori """

        self.plt_target_lsb.append(self.vbus_pid.target_lsb)
        self.plt_reference_lsb.append(self.vbus_pid.reference_lsb)
        self.plt_target_volt.append(self.vbus_pid.target_volt)
        self.plt_reference_volt.append(self.vbus_pid.reference_volt)