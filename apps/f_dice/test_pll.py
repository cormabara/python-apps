from matplotlib import pyplot as plt

from matplotlib import pyplot as plt

from f_dice.lib.tools import SinForm, MyPlot
from f_dice.modules.pll import PhasesPll

test_pll = PhasesPll()
test_pll.SetStimulus(SinForm(0, 720))

myPlot = MyPlot(1, 1, 1, "pll", test_pll.input.phaseIn[:, 0], test_pll.input.phaseIn[:, 1], None, None)
myPlot.show()
