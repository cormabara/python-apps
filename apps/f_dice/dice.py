"""
This is the main file for f_dice device simulator
"""
from enum import Enum,IntEnum

class Platforms(Enum):
    ALICONV = "ALICONV"
    ISDPRO = "ISDPRO"

#
class WorkMode(Enum):
    THEORICAL = "THEORICAL"
    REAL = "REAL"

class Dice:

    def __init__(self, mode_: WorkMode):
        work_mode: WorkMode = mode_
                