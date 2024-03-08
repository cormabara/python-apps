""" Modulo igbt bridge.
    Questo modulo riceve in ingresso:
    - Angolo theta dal modulo VMAINS
    - Iq dal modulo VBUS
    - Genera un PWM per il ponte IGBT che a sua volta genera la vbus """
from my_pid import MyPid


class IgbtBridge:

    def __init__(self, rm_=False):
        self.rm = rm_
        self.enabled = False
        self.pid = MyPid(rm_)

    def init(self):
        pass

    def start(self):
        pass

    def hande(self,theta,id_ref_):
        if not self.enabled:
            # Se il ponte non è abilitato allora si comporta come un normale raddrizzatore
            effort = self.pid.output(id_ref - id_fbk)
        else:
            # Se invece abilitato il pipd lavora e genera pwm che a sua volta controlla il contributo sulla Vbus
            pass

    def background(self):
        pass