import pandas


class MyCsv:

    def __init__(self, filename_):
        self.filename = filename_


class OscilloCsv(MyCsv):

    def __init__(self, filename_):
        MyCsv.__init__(filename_)
        self.data = pandas.read_csv(filename_, header=12).to_numpy()
