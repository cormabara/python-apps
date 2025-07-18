""" Model of the sigma delta converter """


class SigmaDelta:
    """ This is the model for a generic sigma delta device """
    def __init__(self,maxamplitude_, resolution_):
        self.max_amplitude = maxamplitude_
        self.resolution = resolution_

    def calculate(self,in1_,in2_):
        return (in1_ - in2_) * (2**self.resolution)/self.max_amplitude

    def v_2_lsb(self,v_):
        return (v_ * (2**self.resolution))/self.max_amplitude

    def lsb_2_v(self,lsb_):
        return (lsb_ * self.max_amplitude) / (2**self.resolution)
