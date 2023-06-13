"""
In this module the definition of the DICE RECTIFIER application
"""
from dataclasses import dataclass
from mb_dice_lib.pid import DicePid

from f_dice.modules.scr import ScrBridge
from f_dice.lib.tools import SinForm


class InPhasesPll:

    @dataclass
    class Inputs:
        phU: int
        phV: int
        phW: int

    @dataclass
    class Outputs:
        mainVBus: int

    def __init__(self):
        self.scr = ScrBridge()


class VbusPid:

    def __init__(self):
        self.pid = DicePid()
        pass


class CurrentControl:

    def __init__(self):
        self.enabled = False
        self.teta = 0

    def Loop(self):
        if self.enabled:
            self.teta = self._GetTeta()
        else:
            self.teta = 0;

    def _GetTeta(self):
        """ This function return the angle for the current control loop"""
        return 0


class AfeRectifier:

    def __init__(self):
        # inputs
        phaseW = SinForm(0, 720)
        phaseV = SinForm(120, 720)
        phaseW = SinForm(120, 720)

        # outputs
        phaseR = 0
        phaseS = 0
        phaseT = 0
        VBus = 0

        currControl = CurrentControl()
        vbusPid = VbusPid()

    def execute(self):
        pass


