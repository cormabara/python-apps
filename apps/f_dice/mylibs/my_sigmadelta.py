""" Model of the sigma delta converter """


class SigmaDelta:
    """ This is the model for a generic sigma delta device """
    def __init__(self):


    def calculate(self,in1_,in2_):
        return in1_ - in2_

    def loop(self,sample1_,sample2_):
        return sample1_ - sample2_