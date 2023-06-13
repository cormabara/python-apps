"""
This module contain the model for the new PLL on the input phases
"""

from dataclasses import dataclass
from typing import List


class PhasesPll:

    @dataclass
    class Input:
        phaseIn: List[List[float]]

    @dataclass
    class Output:
        phaseOut: List[List[float]]

    def __init__(self):
        self.input = PhasesPll.Input(None)
        pass

    def SetStimulus(self, input_):
        self.input.phaseIn = input_




