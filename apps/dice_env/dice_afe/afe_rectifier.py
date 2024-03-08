"""
In this module the definition of the DICE RECTIFIER application
"""
from enum import Enum, IntEnum

from afe_config import board_set_alarm, Alarms
from modules.mod_igbt_bridge import IgbtBridge
from modules.mod_vbus import ModVBus
from modules.mod_vmains import VMains
from my_timers import SysTimer
from report import MyReport






class AfeRectSt(IntEnum):
    aferect_st_init = 0
    aferest_st_start = 1
    aferect_st_tooperative1 = 2
    aferect_st_tooperative2 = 3
    aferect_st_operative = 4
    aferect_st_fault = 5

class AfeRect:

    TIMEOUT_INIT = 1000
    TIMEOUT_START = 1000
    TIMEOUT_OPERATIVE1 = 1000

    def __init__(self,rm_=False):
        self.status = AfeRectSt.aferect_st_init
        self.state_timer = SysTimer()

        rm = rm_
        self.vmains = VMains(rm_)
        self.vbus = ModVBus(rm_)
        self.bridge = IgbtBridge(rm_)

    def handle(self, in_rt_lsb_, in_st_lsb_):
        """ This is the real time execution of the AFE (normally under 100uS irw)
            the vmains and vbus handle start to work only if the start status is reached """
        if self.status >= AfeRectSt.aferest_st_start:
            self.vmains.handle(in_rt_lsb_, in_st_lsb_)
            self.vbus.handle()

        self.plot_sample()  # Aggironamento dei vettori per il plot

    def _state_machine(self):

        def _state_change(self, new_):
            self.status = new_

        match self.status:

            case AfeRectSt.aferect_st_init:
                """ Stato di inizializzazione con la configurazione dei dispositivi """
                self.state_timer.start(self.TIMEOUT_INIT)
                self.vmains.init()
                self.vbus.init()
                self.bridge.init()
                if self.state_timer.expired():
                    board_set_alarm(Alarms.afe_al_init, "Timeout init scaduto\n")
                else:
                    _state_change(self, AfeRectSt.aferest_st_start)
                    # Questo timer aggiunge un delay tra la init e la start
                    self.state_timer.start(self.TIMEOUT_START)

            case AfeRectSt.aferest_st_start:
                """ Qui viene dato lo start al rettificatore """
                if self.state_timer.expired():
                    self.vmains.start()
                    self.vbus.start()
                    self.bridge.start()
                    self.state_timer.start(self.TIMEOUT_OPERATIVE1)
                    _state_change(self, AfeRectSt.aferect_st_tooperative1)

            case AfeRectSt.aferect_st_tooperative1:
                vac = self.vmains.get_vac()
                if self.vmains.check_input():
                    board_set_alarm(Alarms.afe_al_inputNotOk,"Allarme ingressi VMAINS non OK\n")

                # Se la Vbus e' stabile allora posso passare allo stadio successivo
                vbus_stable = self.vbus.check_vbus_stable(vac)
                if vbus_stable:
                    _state_change(self, AfeRectSt.aferect_st_tooperative2)
                # Se scade timeout errore vbus non stabilizzata in tempo
                if self.state_timer.expired():
                    board_set_alarm(Alarms.afe_al_vbusNotStable, "VBUS is not stable\n")

            case AfeRectSt.aferect_st_tooperative2:
                _state_change(self,AfeRectSt.aferect_st_operative)

            case AfeRectSt.aferect_st_operative:
                pass

            case AfeRectSt.aferect_st_fault:
                pass

    def background(self):
        """ This is the background function called under main with relaxed timings """
        self._state_machine()
        pass

    def plot_sample(self):

        pass

