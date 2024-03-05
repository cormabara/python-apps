"""
In this module the definition of the DICE RECTIFIER application
"""

from modules.vmains import VMains


class AfeRectifier:

    def __init__(self):
        self.vmains = VMains()

    def start(self):
        self.vmains.start()
        pass

    def execute(self, ph_r_, ph_s_, ph_t_):
        self.vmains.execute(ph_r_, ph_s_, ph_t_)
        pass

    def plot_sample(self):

        pass

